#!/usr/bin/env python3.6
# Save proxy clip list

import glob
import os
import pathlib
import shutil
import sys
import time
import tkinter
import tkinter.messagebox
import traceback

import yaml
from celery import group
from colorama import Fore, init
from pyfiglet import Figlet
from win10toast import ToastNotifier

from python_get_resolve import GetResolve
from link_proxies import get_timelines, match_proxies

#'tasks' python file matches 'tasks' variable. 
# Want to keep app terminology close to Celery's.
from proxy_encoder import tasks as do 

# Get environment variables #########################################
script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "proxy_encoder", "config.yml")) as file: 
    config = yaml.safe_load(file)
    
acceptable_exts = config['filters']['acceptable_exts']
proxy_path_root = config['paths']['proxy_path_root']
revision_sep = config['paths']['revision_sep']

debug = False

#####################################################################

# TODO:
# Find out the up to date config setting for 'FORKED_BY_MULTIPROCESSING'

def app_exit(level):
    ''' Standard exitcodes for 'level' '''
    print(f.renderText("Done!"))

    if debug or level > 1: input("Press ENTER to exit.")
    else: exit_in_seconds(seconds = 5)

def toast(message, threaded = True):
    toaster.show_toast(
        "Queue Proxies", 
        message, 
        # icon_path = icon_path, 
        threaded = threaded,
    )
    return

def exit_in_seconds(seconds=5, level=0):
    ''' Allow time to read console before exit '''

    ansi_colour = Fore.CYAN
    if level > 0: ansi_colour = Fore.RED

    for i in range(seconds, -1, -1):
        sys.stdout.write(f"{ansi_colour}\rExiting in " + str(i))
        time.sleep(1)
        
    erase_line = '\x1b[2K' 
    sys.stdout.write(f"\r{erase_line}")
    print()
    sys.exit(level)

def create_tasks(clips, **kwargs):
    ''' Create metadata dictionaries to send as Celery tasks' '''

    # Append project details to each clip
    tasks = [dict(item, **kwargs) for item in clips]
    return tasks

def queue_job(tasks):
    ''' Send tasks as a celery job 'group' '''

    # Wrap job object in task function
    callable_tasks = [do.encode.s(x) for x in tasks]
    if debug: print(callable_tasks)


    # Create job group to retrieve job results as batch
    job = group(callable_tasks)

    # Queue job
    print(f"{Fore.CYAN}Sending job.")
    return job.apply_async()

def link(media_list):

    print(f"{Fore.CYAN}Linking {len(media_list)} proxies.")
    existing_proxies = []

    for media in media_list:
        proxy = media.get('Existing Proxy', None)
        if proxy == None:
            continue

        existing_proxies.append(proxy)

        if not os.path.exists(proxy):
            tkinter.messagebox.showerror(title = "Error linking proxy", message = f"Proxy media not found at '{proxy}'")
            print(f"{Fore.RED}Error linking proxy: Proxy media not found at '{proxy}'")
            continue

        else:
            media.update({'Existing Proxy': None}) # Set existing to none once linked
            media.update({'Proxy':"1280x720"})

    # Match all timelines just in case
    # we've since changed timelines during encode.
    for timeline in get_timelines(active_only=False):
        match_proxies(timeline, existing_proxies)

    print()
    return media_list

def confirm(title, message):
    '''General tkinter confirmation prompt using ok/cancel.
    Keeps things tidy'''

    answer = tkinter.messagebox.askokcancel(
        title = title, 
        message = message,
    )

    some_action_taken = True
    return answer

def get_expected_proxy_path(media_list):
    '''Retrieves the current expected proxy path using the source media path.
    Useful if you need to handle any matching without 'Proxy Media Path' values from Resolve.'''

    for media in media_list:

        file_path = media['File Path']
        p = pathlib.Path(file_path)

        # Tack the source media relative path onto the proxy media path
        expected_proxy_path = os.path.join(proxy_path_root, os.path.dirname(p.relative_to(*p.parts[:1])))
        media.update({'Expected Proxy Path': expected_proxy_path})

    return media_list

def handle_orphaned_proxies(media_list):
    '''Prompts user to tidy orphaned proxies into the current proxy path structure.
    Orphans can become separated from a project if source media file-path structure changes.
    Saves unncessary re-rendering time and lost disk space.'''

    print(f"{Fore.CYAN}Checking for orphaned proxies.")
    orphaned_proxies = []

    for clip in media_list:
        if clip['Proxy'] != "None" or clip['Proxy'] == "Offline":
            linked_proxy_path = os.path.splitext(clip['Proxy Media Path'])
            linked_proxy_path[1].lower()

            file_path = clip['File Path']
            p = pathlib.Path(file_path)

            # Tack the source media relative path onto the proxy media path
            output_dir = os.path.join(proxy_path_root, os.path.dirname(p.relative_to(*p.parts[:1])))
            new_output_path = os.path.join(output_dir, os.path.basename(file_path))
            new_output_path = os.path.splitext(new_output_path)
            new_output_path[1].lower()

            if linked_proxy_path[0] != new_output_path[0]:
                
                # Rejoin extensions 
                linked_proxy_path = ''.join(linked_proxy_path)
                new_output_path = ''.join(new_output_path)

                orphaned_proxies.append({'Old Path': linked_proxy_path, 
                                        'New Path': new_output_path,
                                        })

    if len(orphaned_proxies) > 0:
        
        some_action_taken = True
        print(f"Orphaned proxies: {len(orphaned_proxies)}")
        answer = tkinter.messagebox.askyesnocancel(title="Orphaned proxies",
                                        message=f"{len(orphaned_proxies)} clip(s) have orphaned proxy media. " +
                                        "Would you like to attempt to automatically move these proxies to the up-to-date proxy folder?\n\n" +
                                        "For help, check 'Managing Proxies' in our YouTour documentation portal.")
        if answer == True:
            for proxy in orphaned_proxies:

                output_folder = os.path.dirname(proxy['New Path'])
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

                shutil.move(proxy['Old Path'], proxy['New Path'])


        elif answer == None:
            print("Exiting...")
            sys.exit(1)

    else:
        print(f"{Fore.GREEN}Found none.")
    
    print()
    return media_list
    
def handle_already_linked(media_list):
    '''Remove media from the queue if the source media already has a linked proxy that is online.
    As re-rendering linked clips is rarely desired behaviour, it makes sense to avoid clunky prompting.
    To re-render linked clips, simply unlink their proxies and try queueing proxies again. 
    You'll be prompted to handle offline proxies.'''

    print(f"{Fore.CYAN}Checking for source media with linked proxies.")
    already_linked = [x for x in media_list if x['Proxy'] != "None"]

    if len(already_linked) > 0:
        
        some_action_taken = True
        print(f"{Fore.YELLOW}Skipping {len(already_linked)} already linked.")
        media_list = [x for x in media_list if x not in already_linked]

    else:
        print(f"{Fore.GREEN}Found none.")

    print()
    return media_list

def handle_offline_proxies(media_list):

    print(f"{Fore.CYAN}Checking for offline proxies")
    offline_proxies = [x for x in media_list if x['Proxy'] == "Offline"]

    if len(offline_proxies) > 0:

        some_action_taken = True

        print(f"{Fore.CYAN}Offline proxies: {len(offline_proxies)}")
        answer = tkinter.messagebox.askyesnocancel(title="Offline proxies",
                                        message=f"{len(offline_proxies)} clip(s) have offline proxies.\n" +
                                        "Would you like to rerender them?")


        if answer == True:
            print(f"{Fore.YELLOW}Rerendering offline: {len(offline_proxies)}")
            # Set all offline clips to None, so they'll rerender
            # [media['Proxy'] == "None" for media in media_list if media['Proxy'] == "Offline"]
            for media in media_list:
                if media['Proxy'] == "Offline":
                    media['Proxy'] = "None"


        if answer == None:
            print(f"{Fore.RED}Exiting...")
            sys.exit(0)
    else:
        print(f"{Fore.GREEN}Found none.")
    
    print()
    return media_list

def handle_existing_unlinked(media_list):
    '''Prompts user to either link or re-render proxy media that exists in the expected location, 
    but has either been unlinked at some point or was never linked after proxies finished rendering.
    Saves confusion and unncessary re-rendering time.'''

    print(f"{Fore.CYAN}Checking for existing, unlinked media.")
    existing_unlinked = []

    
    get_expected_proxy_path(media_list)

    for media in media_list:
        if media['Proxy'] == "None":

            some_action_taken = True
            expected_proxy_path = media['Expected Proxy Path']
            media_basename = os.path.splitext(os.path.basename(media['File Name']))[0]
            expected_proxy_file = os.path.join(expected_proxy_path, media_basename)
            expected_proxy_file = os.path.splitext(expected_proxy_file)[0]
            
            existing = glob.glob(expected_proxy_file + "*.*")

            if len(existing) > 0:


                try:
                    existing.sort(key=os.path.getmtime)
                    # if debug: print(f"{Fore.MAGENTA} [x] Found {len(existing)} existing matches for {media['File Name']}")
                    existing = existing[0]
                    # if debug: print(f"{Fore.MAGENTA} [x] Using newest: '{existing}'")
                except:
                    # if debug: print(f"{Fore.MAGENTA} [x] {Fore.YELLOW}Couldn't sort by modification time.")
                    sorted(existing, key = lambda x: int(x.split(revision_sep)[1]))
                    existing = existing[0]
                    # if debug: print(f"{Fore.MAGENTA} [x] Using largest revision number: {existing}")


                media.update({'Existing Proxy': existing})
                existing_unlinked.append(existing)


    if len(existing_unlinked) > 0:
        print(f"{Fore.YELLOW}Found {len(existing_unlinked)} unlinked")
        answer = tkinter.messagebox.askyesnocancel(title="Found unlinked proxy media",
                                        message=f"{len(existing_unlinked)} clip(s) have existing but unlinked proxy media. " +
                                        "Would you like to link them? If you select 'No' they will be re-rendered.")

        if answer == True:
            link(media_list)

            # Remove the proxies we just linked from the media_list
            pre_len = len(media_list)

            media_list = [x for x in media_list if 'Existing Proxy' not in x]

            post_len = len(media_list)
            print(f"{pre_len - post_len} proxy(s) linked, will not be queued.")
            print(f"{Fore.MAGENTA}Queueing {post_len}")
            
        
        elif answer == False:
            print(f"{Fore.YELLOW}Existing proxies will be OVERWRITTEN!")

        else:
            print("Exiting...")
            sys.exit(0)

    else:
        print(f"{Fore.GREEN}Found none.")
    
    print()
    return media_list

def get_media():
    ''' Main function to get clip-list and prompt user to filter passed clips.'''

    track_len = timeline.GetTrackCount("video")
    if track_len == 1: 
        # Really not sure why, but Resolve returns no clips if only one vid timeline
        message = "Not enough tracks on timeline to get clips.\nPlease create another empty track"
        print(f"\nERROR:\n{message}")
        tkinter.messagebox.showinfo("ERROR", message)
        sys.exit(1)
        
    print(f"{Fore.GREEN}Video track count: {track_len}")

    all_clips = []
    for i in range(1, track_len):
        items = timeline.GetItemListInTrack("video", i)
        
        if items is None:
            print(f"No items found in track {i}")
            continue
        
        for item in items:
            for ext in acceptable_exts:
                if ext.lower() in item.GetName().lower():
                    try:

                        media_item = item.GetMediaPoolItem()
                        attributes = media_item.GetClipProperty()
                        all_clips.append(attributes)

                    except:
                        print(f"Skipping {item.GetName()}, no linked media pool item.")    
                        continue

    # Get unique source media from clips on timeline
    unique_sets = set(frozenset(d.items()) for d in all_clips)
    media_list = [dict(s) for s in unique_sets]

    print(f"{Fore.GREEN}Total clips on timeline: {len(all_clips)}")
    print(f"{Fore.GREEN}Unique source media: {len(media_list)}")
    print()


    media_list = handle_orphaned_proxies(media_list)
    media_list = handle_already_linked(media_list)
    media_list = handle_offline_proxies(media_list)
    media_list = handle_existing_unlinked(media_list)


    return media_list

if __name__ == "__main__":

    init(autoreset=True)
    toaster = ToastNotifier()
    
    root = tkinter.Tk()
    root.withdraw()

    some_action_taken = False

    f = Figlet()
    print(f.renderText("Queue/Link Proxies"))
    
    try:       
        # Get global variables
        resolve = GetResolve()
        project = resolve.GetProjectManager().GetCurrentProject()
        timeline = project.GetCurrentTimeline()     

        print()
        # HEAVY LIFTING HERE
        clips = get_media()

        if len(clips) == 0:
            if not some_action_taken:
                print(f"{Fore.RED}No clips to queue.")
                tkinter.messagebox.showwarning("No clip to queue", "There is no new media to queue for proxies.\n" +
                                            "If you want to re-rerender some proxies, unlink those existing proxies within Resolve and try again.")
                sys.exit(1)
            else:
                print(f"{Fore.GREEN}All clips linked now. No encoding necessary.")

        # Final Prompt confirm
        if not confirm(
            "Go time!", 
            f"{len(clips)} clip(s) are ready to queue!\n" +
            "Continue?"
        ):
            sys.exit(0)

        tasks = create_tasks(
            clips,
            project = project.GetName(), 
            timeline = timeline.GetName(),
        )

        job = queue_job(tasks)

        toast('Started encoding job')
        print(f"{Fore.YELLOW}Waiting for job to finish. Feel free to minimize.")
        
        job_metadata = job.join()

        # Notify failed
        if job.failed():
            fail_message = f"Some videos failed to encode! Check dashboard @ 192.168.1.19:5555."
            print(Fore.RED + fail_message)
            toast(fail_message)

        # Notify complete
        complete_message = f"Completed encoding {job.completed_count()} videos."
        print(Fore.GREEN + complete_message)
        print()

        toast(complete_message)

        # ATTEMPT POST ENCODE LINK
        active_project = resolve.GetProjectManager().GetCurrentProject().GetName()
        linkable = [x for x in job_metadata if x['project'] == active_project]

        if len(linkable) == 0:
            print(
                f"{Fore.YELLOW}\nNo proxies to link post-encode.\n" +
                "Resolve project may have changed.\n" +
                "Skipping."
            )

        else: 
            link(linkable)

        app_exit(0)

    
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        
        tkinter.messagebox.showerror("ERROR", tb)
        print("ERROR - " + str(e))

        app_exit(1)
