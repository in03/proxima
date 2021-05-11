
#!/usr/bin/env python3.6
# Link proxies

import os, re
import traceback
import tkinter
import tkinter.messagebox
import yaml
from tkinter import filedialog

from python_get_resolve import GetResolve
from datetime import datetime
from colorama import init, Fore

# Get environment variables #########################################
script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "proxy_encoder", "config.yml")) as file: 
    config = yaml.safe_load(file)
    
proxy_path_root = config['paths']['proxy_path_root']
acceptable_exts = config['filters']['acceptable_exts']

#####################################################################

debug = False
      
# Get global variables
resolve = GetResolve()
project = resolve.GetProjectManager().GetCurrentProject()
media_pool = project.GetMediaPool()


def get_proxy_path():
    root = tkinter.Tk()
    root.withdraw()
    f = filedialog.askdirectory(initialdir = proxy_path_root, title = "Link proxies")
    if f is None:
        print("User cancelled dialog. Exiting.")
        exit(0)
    return f

def filter_videos(dir):
    videos = []

    # Walk directory to match files
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in files:
            file = os.path.join(root, name)
            # print(file)

            # Check extension is allowed
            if os.path.splitext(file)[1].lower() in acceptable_exts:
                videos.append(file)
    return videos

def match_proxies(timeline, potential_proxies):

    linked = []

    track_len = timeline.GetTrackCount("video")
    if track_len < 1:
        raise Exception(f"Please add another empty video track\n." +
                        "Resolve needs at least two to export a clip-list.")

    print(f"{Fore.CYAN}{timeline.GetName()} - Video track count: {track_len}")
    for i in range(track_len):
        items = timeline.GetItemListInTrack("video", i)
        if items is None:
            continue

        for potential_proxy in potential_proxies:
            proxy_name = os.path.splitext(os.path.basename(potential_proxy))[0]
            if debug: print(f"Potential proxy: {proxy_name}")

            for item in items:
                for ext in acceptable_exts:
                    if ext.lower() in item.GetName().lower():
                        try:
                            media = item.GetMediaPoolItem()
                            name = media.GetName()
                            path = media.GetClipProperty("File Path")

                        except:
                            print(f"Skipping {item.GetName()}, no linked media pool item.")
                            continue
                        
                        clip_name = os.path.splitext(os.path.basename(path))[0]
                        if proxy_name.lower() in clip_name.lower():
                            if name not in linked:
                                linked.append(name)
                                print(f"{Fore.GREEN}Found match: {path} & {potential_proxy}")
                                media.LinkProxyMedia(potential_proxy)

                                # if media.LinkProxyMedia(potential_proxy):
                                #     print(f"Linked: {proxy_name}")
                                # else:
                                #     raise Exception(f"Couldn't link proxy: {proxy_name}")

def get_timelines(active_only=False):

    if active_only:
        ct = project.GetCurrentTimeline()
        print(f"{Fore.YELLOW}Linking for active timeline: '{ct.GetName()}' only")
        return [ct]

    print(f"{Fore.YELLOW}Linking for all non-revision timelines")

    main = []
    revisions = []

    tc = project.GetTimelineCount()
    for i in range(1, tc + 1):
        timeline = project.GetTimelineByIndex(i)
        tn = timeline.GetName()
        if tn is not None:
            if re.search(r"^(\w+)(\s)(V\d+)", tn, re.IGNORECASE):
                revisions.append(tn)
            else:   
                main.append(timeline)
    
    if debug: print(f"{Fore.YELLOW}Skipped linking identified revisions to save time: {revisions}")
    if debug: print(f"{Fore.CYAN}Attempting to match proxies for timelines: {main}")
    return main
    

if __name__ == "__main__":

    try:
        init(autoreset=True)

        proxy_dir = get_proxy_path()
        print(f"Passed directory: '{proxy_dir}'\n")

        potential_proxies = filter_videos(proxy_dir)
        print(potential_proxies, "\n")
    
        # TODO: Work on this a little
        for timeline in get_timelines(active_only=True): 
            print("")
            match_proxies(timeline, potential_proxies)

    
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        tkinter.messagebox.showinfo("ERROR", tb)
        print("ERROR - " + str(e))