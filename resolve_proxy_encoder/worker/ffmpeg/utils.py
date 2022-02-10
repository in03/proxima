from ffmpeg import probe


class FileInfoProvider:
    def __init__(self, video_path):
        self._video_path = video_path

    def get_bitrate(self, decimal_places, video_path=None):
        if video_path:
            bitrate = probe(video_path)["format"]["bit_rate"]
        else:
            bitrate = probe(self._video_path)["format"]["bit_rate"]
        return (
            f"{force_decimal_places((int(bitrate) / 1_000_000), decimal_places)} Mbps"
        )

    def get_framerate_fraction(self):
        r_frame_rate = [
            stream
            for stream in probe(self._video_path)["streams"]
            if stream["codec_type"] == "video"
        ][0]["r_frame_rate"]
        return r_frame_rate

    def get_framerate_float(self):
        numerator, denominator = self.get_framerate_fraction().split("/")
        return int(numerator) / int(denominator)

    def get_duration(self):
        return float(probe(self._video_path)["format"]["duration"])
