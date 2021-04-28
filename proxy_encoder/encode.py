# transcodable_files = list(filter(lambda f: os.path.splitext(f)[1].lower() in allowed_ext, files_to_encode))



import glob
import os
import pathlib
import re
import subprocess
import sys
import winsound
from datetime import datetime
from winsound import Beep

import yaml
from colorama import Fore, Style, init
from natsort import natsorted

# Get environment variables #########################################
script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "config.yml")) as file: 
    config = yaml.safe_load(file)
    
ffmpeg_path = config['paths']['ffmpeg']
proxy_path_root = config['paths']['proxy_path_root']
acceptable_exts = config['filters']['acceptable_exts']
revision_sep = config['paths']['revision_sep']
status_whitelist = config['filters']['status_whitelist']
cwd = os.getcwd()

default = config['default']
debugmode = config['debugmode']
job_ext = ".yml"

#####################################################################

def main_init():
    ''' Run general init stuff'''

    global print_path

    # printging path
    if not os.path.exists(proxy_path_root):
        raise Exception(f"{proxy_path_root} does not exist. Please check write path.")
    print_path = os.path.join(proxy_path_root, "ProxyEncoder.print")

    new_job = f"################# {datetime.now().strftime('%A, %d, %B, %y, %I:%M %p')} #################"
    print(new_job)

def filter_by_status(media, status_whitelist, warn=False):
    '''Remove jobs that aren't in an encodable state'''
    ready = [x for x in media if x['status'].casefold() in status_whitelist.casefold()]

    if warn:
        not_ready = [x for x in media if x not in ready]
        for x in not_ready:
            print(f"{Fore.YELLOW}{x['project']} - {x['timeline']} from yaml file has status:{Fore.RED}'{x['status'].upper()}'\n" +
                    "Skipping. If you want to run it anyway, add the '--force' flag.")
    return ready
    
def get_vids(jobs):
    ''' Get encodable files from yaml'''

    encodable = []
    
    for job in jobs:
        if not job['File Path']:
            print(f"{job} has no file path. Skipping.")
            continue
        
        source_media = job['Source Media']


        print(f"Checking path: '{source_media}'")
        if os.path.isfile(source_media):
            if os.path.splitext(source_media)[1].casefold() in acceptable_exts:
                
                # Get folder structure
                p = pathlib.Path(source_media)
                output_dir = os.path.join(proxy_path_root, os.path.dirname(p.relative_to(*p.parts[:1])))
                # Make folder structure
                os.makedirs(output_dir, exist_ok=True)
                # Return full output file path
                output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(source_media))[0])

                # Append additional args if necessary
                if type(source_media) is dict:
                    output_dict = {"output_file":output_file}
                    media_dict = dict(source_media, **output_dict)
                else:
                    media_dict = {"path":source_media, "output_file":output_file}

                encodable.append(media_dict)

    return encodable

def get_next_revision(media):
    '''Get the next version number for a colliding file to increment'''

    expected_proxy_path = media['Expected Proxy Path']
    media_basename = os.path.splitext(os.path.basename(media['File Name']))[0]
    expected_proxy_file = os.path.join(expected_proxy_path, media_basename)
    expected_proxy_file = os.path.splitext(expected_proxy_file)[0]
    print(expected_proxy_file)

    existing = glob.glob(expected_proxy_file + "*.*") # TODO: This always fails

    if len(existing) > 1:

        revisions = []
        for media in existing:

            path = os.path.dirname(media)
            filename = os.path.basename(media)

            if debugmode: print(f"Checking filename '{filename}' for suffix")

            regex_pattern = rf"({revision_sep}[0-9]+)*$"
            if debugmode: print(f"Regex search pattern: {regex_pattern}")
        
            if re.search(regex_pattern, path, re.IGNORECASE):
                if debugmode: print(f"File '{filename}' has suffix. Adding for compare.")
                revisions.append(filename)
            else:
                if debugmode: print(f"File '{filename}' has no suffix.")

            if len(revisions) > 0:

                # Get last revision of all
                if debugmode: print(f"Revisions:\n{revisions}")
                lr = natsorted(revisions).pop()
                if debugmode: print(f"Last revision: {lr}")
                
                # Increment revision
                nr = re.sub(r"([0-9]+)*$", 
                        lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",  
                        lr)
                        
                nr = str(nr)
                if debugmode: print(f"New revision: {nr}")
                return os.path.join(path, nr)

    # If none exist, start first
    if debugmode: print("Starting first revision")
    existing = os.path.splitext(existing[0])
    nr = existing[0] + "_1" + existing[1]
    return os.path.join(path, nr)

def handle_clip_args(file):
    # Add handling for wanted args here #############################
    args = []

    try:
        if file['V-FLIP'] == "On": args.append("vflip")
        if file['H-FLIP'] == "On": args.append("hflip")

    except KeyError as key_error:
        print(f"Missing key for extra arg: {key_error}")

    # Convert filter args from clip attributes to comma separated string
    if len(args) > 0:
        return "," + ','.join(map(str, args))
    return ""
    #####################################################

def handle_overwriting(encodable):
    '''Increment filenames, overwrite or skip clips that already exist on disk'''
    for video in encodable:

        dst = os.path.splitext(video['output_file'])[0] + default['ext']
        dst_name = os.path.basename(dst)

        print(f"Checking if '{dst_name}' exists on disk already.")

        if os.path.exists(dst):

            if args.increment:
                print(f"{Fore.YELLOW}'{dst}' already exists on disk\nWill increment.\n")
            
                nr = get_next_revision(video)
                print(f"Added suffix: '{os.path.basename(nr)}'")
                video['output_file'] = os.path.splitext(nr)[0]

            elif not args.keep:
                print(f"{Fore.YELLOW}Proxy file '{dst}' already exists on disk. OVERWRITING!")
                
            else:
                print(f"{Fore.YELLOW}Proxy file '{dst}' already exists on disk. Skipping encode.")
                encodable = [x for x in encodable if video in encodable]
    return encodable

def render(job_file):

    # Get args
    src_path = job_file['File Path']
    output_path = job_file['output_file']
    default = config['default']

    print("\n")    

    try:
        ffmpeg = os.path.join(ffmpeg_path, "ffmpeg.exe")
        
        # FILTER ARGS
        resolution = f"scale={default['h_res']}:{default['v_res']}"
        framerate = f"fps={job_file.get('FPS', default['framerate'])}"
        pix_fmt = f"format={default['pix_fmt']}"
        clip_args = handle_clip_args(job_file)
        
        # In case clip_args is empty, no comma below, comma is prepended in func
        filter_args = f"-vf {resolution},{framerate},{pix_fmt}{clip_args}"

        vid_args = f"-c:v {default['vid_codec']} -profile:v {default['vid_profile']} {filter_args}"
        audio_args = f"-c:a {default['audio_codec']} -ar {default['audio_samplerate']}"
        misc_args = " ".join(default['misc_args'])

        cmd = f"\"{ffmpeg}\" -y -i \"{src_path}\" {vid_args} {audio_args} {misc_args} \"{output_path}{default['ext']}\""
        print(f"Full command:\n{cmd}\n")

        if debugmode:
            print(f"{Fore.YELLOW}Dryrun enabled! Printing command only:")
            print(cmd)
            return True
        else:
            print(f"{Fore.CYAN}Encoding {Style.RESET_ALL}'{job_file['File Path']}'")

        subprocess.call(cmd, shell=True,
        start_new_session = True, stderr=subprocess.STDOUT, 
        universal_newlines=True)

    except subprocess.CalledProcessError as exc:
        print("\n\n----------------------------")
        print(Fore.RED + "FAILED:\n", exc.returncode, exc.output)
        print(f"Failed encoding: {src_path}")
        print("----------------------------\n\n")
        winsound.Beep(375, 150) # Fail beep
        return False

    else:
        winsound.Beep(600, 200) # Success beep
        return True
 
def encode(paths):

    encodable = get_vids(paths)

    # Exit if none
    if len(encodable) == 0:
        print(Fore.RED + "No encodable files passed.")
        sys.exit(1) 

    [print(f"{Fore.YELLOW}Queued {x['File Path']}") for x in encodable]

    encodable = handle_overwriting(encodable)

    # Encode all files
    for file in encodable:
        if encode(file):
            print(Fore.GREEN + "Successfully encoded")

    print(f"{Fore.GREEN}Done encoding. Check print file: '{print_path}'\n")

    # Finished jingle
    for i in range(1, 10):
        winsound.Beep(i * 100, 200)


    # Get encodable files from text `clip` list
    skipped, encodable_from_yml = get_vids(yml_media)

    # Get any dirs, files passed for processing
    skipped, encodable_loose = get_vids(filepaths)

    # Combine and dedupe encode lists
    encodable = dedupe(encodable_from_yml + encodable_loose)

    # Exit if none
    if len(encodable) == 0:
        print(Fore.RED + "No encodable files passed.")
        sys.exit(1) 

    for video in encodable: print(f"{Fore.YELLOW}Queued {video['File Path']}")


    # Handle overwriting
    for video in encodable:

        dst = os.path.splitext(video['output_file'])[0] + default['ext']
        dst_name = os.path.basename(dst)

        print(f"Checking if '{dst_name}' exists on disk already.")

        if os.path.exists(dst):

            if args.increment:
                print(f"{Fore.YELLOW}'{dst}' already exists on disk\nWill increment.\n")
            
                nr = get_next_revision(video)
                print(f"Added suffix: '{os.path.basename(nr)}'")
                video['output_file'] = os.path.splitext(nr)[0]

            elif not args.keep:
                print(f"{Fore.YELLOW}Proxy file '{dst}' already exists on disk. OVERWRITING!")

                # send2trash(dst + default['.mxf']) # Not necessary to trash. Causes more problems with file permissions.
                # Just overwrite file straight. But be careful you don't overwrite the wrong file, you'll never get it back.
                
            else:
                print(f"{Fore.YELLOW}Proxy file '{dst}' already exists on disk. Skipping encode.")
                encodable.remove(video)

    # Encode all files
    for file in encodable:
        if encode(file):
            print(Fore.GREEN + "Successfully encoded")
            # print(f"{Fore.GREEN}Successfully encoded: {file}\n\n", print_only=args.hidebanner)

    print(f"{Fore.GREEN}Done encoding. Check print file: '{print_path}'\n")

    # Finished jingle
    for i in range(1, 10):
        winsound.Beep(i * 100, 200)
