from __future__ import absolute_import

import logging
import os
import re
import shlex
import shutil
import subprocess
import sys
from collections import Counter

from pymediainfo import MediaInfo

from ..app.utils import core
from ..settings.manager import SettingsManager
from ..worker.celery import app
from ..worker.ffmpeg.ffmpeg_process import FfmpegProcess
from ..worker.ffmpeg.utils import frac_to_dec, frac_to_tc, get_media_info
from ..worker.utils import check_wsl, get_queue, get_wsl_path

config = SettingsManager()

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)


class SplitAndStitch:

    """
    Split a file into frame ranges at a set interval,
    run multiple FFmpeg encodes and stitch into single file once finished.
    """

    def __init__(self, file, dest, chunk_secs):

        self.file = file
        self.dest = dest
        self.chunk_secs = chunk_secs

    def run(self):

        logger.info(f"[green]Got new temporary directory\n{self.temp_working_dir}[/]")

        self.get_temp_dir()
        self.split()
        self.stitch()
        self.move()
        self.del_temp_dir()

    # SPLIT FUNCS ####################################

    def split(self):

        logger.info("[yellow]Calculating chunks :hourglass:")
        self.chunk_data = self.calculate_chunks(self.file, self.chunk_len)

        # TODO: Replace `local_encode_chunks` call with worker encode task
        self.exported_files = self.local_encode_chunks(
            self.chunk_data, self.temp_working_dir
        )
        logger.info(f"[green]Finished encoding chunks[/] :heavy_check_mark:")
        print()

        return self.exported_files

    def calculate_chunks(file, chunk_secs):
        """
        Calculate frame ranges for ffmpeg to split file
        at specified interval. Return a dictionary with a list of
        dictionaries and their chunking data.
        """

        # Get media info
        info = get_media_info(file)
        fps = frac_to_dec(info["streams"][0]["r_frame_rate"])
        nb_frames = int(info["streams"][0]["nb_frames"])

        # Print file metadata

        print()
        logger.info(f"[green]Media Info:[/]")
        logger.info(f"Framerate {fps}")
        logger.info(f"Total frames {nb_frames}")

        print()
        logger.info("[green]chunk Info:[/]")
        chunk_frames = chunk_secs * fps
        logger.info(f"Interval seconds {chunk_secs}, Interval frames {chunk_frames}")

        whole_chunks = int(nb_frames // chunk_frames)
        logger.info(f"Whole chunks: {whole_chunks}")

        partial_chunk_length = float(str(nb_frames / chunk_frames)) % 1
        logger.info(f"Partial chunk remaining frames: {partial_chunk_length}")

        total_chunks = whole_chunks
        if partial_chunk_length > 0:
            total_chunks = whole_chunks + 1

        logger.info(f"Total chunks: {total_chunks}")

        # Init seg vars
        in_point = 0
        out_point = 0
        seg_num = 0
        job = {
            "file": file,
            "chunks": [],
        }

        # Get whole chunks
        # Start at 1 to match total when iterating
        logger.debug(f"Individual chunks:")
        for i in range(1, whole_chunks + 1):

            in_point = out_point
            out_point = in_point + chunk_frames
            seg_num = i

            in_point_tc = frac_to_tc(in_point, fps)
            out_point_tc = frac_to_tc(out_point, fps)

            logger.debug(
                f"Whole {seg_num} in point: {in_point_tc}, out_point: {out_point_tc}"
            )

            job["chunks"].append(
                {
                    "in_point": in_point_tc,
                    "out_point": out_point_tc,
                    "chunk_number": seg_num,
                }
            )

        # If partial chunk, get
        if partial_chunk_length > 0:

            in_point = out_point
            out_point = in_point + (chunk_frames * partial_chunk_length)
            seg_num = seg_num + 1

            in_point_tc = frac_to_tc(in_point, fps)
            out_point_tc = frac_to_tc(out_point, fps)

            logger.debug(
                f"Partial {seg_num}, in point: {in_point_tc}, out_point: {out_point_tc}"
            )

            job["chunks"].append(
                {
                    "in_point": in_point_tc,
                    "out_point": out_point_tc,
                    "chunk_number": seg_num,
                }
            )

        else:

            logger.info(f"[green]Clean chunk division; no partial.")

        logger.info(f"[green]Calculated chunks: {job}")

    def local_encode_chunks(chunk_data, temp_working_dir):
        """Function to encode chunk ranges sequentially.
        Use for testing locally outside of Celery."""

        print()
        logger.info("[green]Encoding Info:[/]")

        # Example syntax:
        # ffmpeg -i input.mp4 -ss 00:00:00 -to 00:10:00 -c copy output1.mp4
        # ffmpeg -i input.mp4 -ss 00:10:00 -to 00:20:00 -c copy output2.mp4

        input_file = chunk_data["file"]
        chunks = chunk_data["chunks"]

        exported_chunks = []

        # Feed chunks
        chunk_len = len(chunks)
        logger.debug(f"Received chunks", chunk_len)
        logger.info(f"[yellow]Encoding chunks :hourglass: ... [/]")

        for chunk in chunks:

            in_point = chunk["in_point"]
            out_point = chunk["out_point"]
            seg_num = chunk["chunk_number"]

            logger.debug(f"chunk data: {chunk}")

            output_filename = os.path.splitext(os.path.basename(input_file))[0]
            output_filename = output_filename + f"-{seg_num}" + ".mxf"
            output_file = os.path.join(temp_working_dir, output_filename)

            # Seeking cannot be accurate with '-c copy', since FFMpeg is forced to cut on I-frames!
            cmd = (
                f'ffmpeg -loglevel error -nostats -ss {in_point} -to {out_point} -i "{input_file}" '
                + f'-c:v dnxhd -profile:v dnxhr_sq -vf "scale=1280:720,fps=50,format=yuv422p" -c:a pcm_s16le -ar 48000 "{output_file}"'
            )

            logger.debug("CMD ->\n" + cmd)
            subprocess.call(cmd, shell=True)
            logger.info(f"Finished chunk {seg_num} :heavy_check_mark:")

            exported_chunks.append(output_file)

        logger.debug(f"Exported chunks: {exported_chunks}")
        return exported_chunks

    # stitch FUNCS ####################################

    def stitch(self):
        """Stitch provided chunks using FFMpeg"""

        logger.info(f"[yellow]Stitching chunks[/] :hourglass: ...")
        sorted_chunks = self.parse_chunks(self.exported_files)
        temp_concat_file = self.make_concat_file(sorted_chunks, self.temp_working_dir)
        self.stitched_file = self.ffmpeg_concat(temp_concat_file, sorted_chunks)
        logger.info(f"[green]Finished stitching chunks :heavy_check_mark:[/]")

        return self.stitched_file

    def parse_chunks(chunks):
        """Check passed files are concatanatable, sort them in order"""

        # Check extensions are the same
        exts = [os.path.splitext(x)[1] for x in chunks]
        if len(Counter(exts)) > 1:
            print(
                "Multiple formats passed: codec, format and extension must be identical!"
            )
            sys.exit(1)

        sorted_segs = sorted(chunks)
        # print(sorted_segs)

        for chunk in sorted_segs:

            incrementals = []
            # Check filenames are incremented by 1, none missing
            match = re.search(config["chunking"]["increment_regex"], chunk)

            if not match:
                logger.error(
                    "File missing incremental! Ensure suffix matches regex set in user settings.\n"
                    + "e.g. '-1.mp4', '-2.mp4', etc."
                )
                core.app_exit(1)

            # incrementals.append(match.group(1))

            # if not list(range(int(incrementals[0]), int(incrementals[-1]) + 1)):
            #     print("Filenames do not increment by 1! Are there clips missing?")
            #     sys.exit(1)

            return sorted_segs

    def make_concat_file(chunks):
        """Create temporary concatentation file for FFmpeg"""

        # Ensure .txt extension
        if not os.path.splitext(filepath)[1]:
            filepath = filepath + ".txt"

        parsed_chunks = [f"file '{os.path.normpath(x)}'\n" for x in chunks]

        with open(filepath, "a") as concat_file:
            concat_file.writelines(parsed_chunks)

        return filepath

    def ffmpeg_concat(filename, chunks):
        """Losslessly stitch file chunks with FFmpeg.
        Output to same path as source chunks"""

        # Get source clip's name and extension for output
        source_name, source_ext = os.path.splitext(chunks[0])

        # Remove increment pattern for output
        output_name = re.sub(
            config["chunking"]["increment_regex"],
            "",
            source_name,
        )

        stitched_file = output_name + config["chunking"]["output_suffix"] + source_ext

        # TODO: Use custom ffmpeg class instead of this subprocess call
        # Concat with FFmpeg
        cmd = f'ffmpeg -y -loglevel error -nostats -f concat -safe 0 -i "{filename}" -c copy "{stitched_file}"'
        logger.debug("CMD -> " + cmd)

        subprocess.call(shlex.split(cmd))

        return stitched_file

    # MOVE FUNCS ####################################

    def move(self):

        """Move the final stitched file to the output destination folder"""

        filename = os.path.basename(self.stitched_file)

        destination_path = os.path.normpath(os.path.join(self.dest, filename))
        logger.info(
            f"[yellow]Moving stitched file: '{os.path.basename(self.stitched_file)} -> '{destination_path}' :hourglass:",
        )

        try:
            shutil.move(self.stitched_file, destination_path)
        except:
            logger.error(
                f"[red]Couldn't move stitched file to destination path[/]{destination_path}"
            )
        else:
            logger.info(f"[green]Successfully moved :heavy_check_mark:[/]")


def split_and_stitch(job):
    # TODO: parse job to create new split and stitch tasks

    file = job["source_media"]
    dest = job["output_file"]
    chunk_secs = config["chunking"]["chunk_secs"]

    split_and_stitch = SplitAndStitch(file, dest, chunk_secs)
    split_and_stitch.run()
