#!/usr/bin/env python3.6
# Save proxy clip list

import glob
import os
import pathlib
import shutil
import sys
import tkinter
import tkinter.messagebox
import traceback

from celery import group
from colorama import Fore

from resolve_proxy_encoder import helpers
from resolve_proxy_encoder.link_proxies import link_proxies

# 'tasks' python file matches 'tasks' variable. 
# Want to keep app terminology close to Celery's.
from resolve_proxy_encoder.proxy_encoder import tasks as do
from resolve_proxy_encoder.proxy_encoder.celery import app
from resolve_proxy_encoder.settings import app_settings

config = app_settings.get_user_settings()

# Get global variables
resolve_obj = helpers.get_resolve_objects()
resolve = resolve_obj['resolve']
project = resolve_obj['project']
timeline = resolve_obj['timeline']
media_pool = resolve_obj['media_pool']

resolve_job_name = f"{project.GetName().upper()} - {timeline.GetName().upper()}"
proxy_path_root = os.path.normpath(config['paths']['proxy_path_root'])

# Prevent TKinter root window showing
root = tkinter.Tk()
root.withdraw()

# Set global flags
global some_action_taken
some_action_taken = False


def create_tasks(clips, **kwargs):
    """ Create metadata dictionaries to send as Celery tasks' """

    # Append project details to each clip
    tasks = [dict(item, **kwargs) for item in clips]
    return tasks

def queue_job(tasks):
    """ Send tasks as a celery job 'group' """

    # Wrap job object in task function
    callable_tasks = [do.encode.s(x) for x in tasks]
    if config['loglevel'] == "DEBUG": print(callable_tasks)


    # Create job group to retrieve job results as batch
    job = group(callable_tasks)

    # Queue job
    print(f"{Fore.CYAN}Sending job.")
    return job.apply_async()

def postencode_link(media_list):
    """ Iterate through media mutated during script call, attempt to link the source media """

    print(f"{Fore.CYAN}Linking {len(media_list)} proxies.")

    link_success = []
    link_fail = []

    # Iterate through all available proxies
    for media in media_list:
        proxy = media.get('Unlinked Proxy', None)
        if proxy == None:
            continue

        # Check they exist
        if not os.path.exists(proxy):
            tkinter.messagebox.showerror(title = "Error linking proxy", message = f"Proxy media not found at '{proxy}'")
            print(f"{Fore.RED}Error linking proxy: Proxy media not found at '{proxy}'")
            continue

        else:
            media.update({'Unlinked Proxy': None}) # Set existing to none once linked

        media.update({'Proxy':"1280x720"})

        # Actually link proxies
        media_pool_item_obj = media['media_pool_item_obj']
        if media_pool_item_obj.LinkProxyMedia(proxy):
            
            #TODO get this working!
            print(f"{Fore.GREEN}Linked {media['File Name']}")
            link_success.append(proxy)

        else:
            print(f"{Fore.RED}Failed link.\n")
            link_fail.append(proxy)

    if link_success:
        print(f"{Fore.GREEN}Succeeeded linking: {len(link_success)}")

    if link_fail:
        print(f"{Fore.RED}Failed linking: {len(link_success)}")

        
    # link_proxies(existing_proxies)

    print()

    pre_len = len(media_list)
    media_list = [x for x in media_list if 'Unlinked Proxy' not in x]
    post_len = len(media_list)
    print(f"{pre_len - post_len} proxy(s) linked, will not be queued.")
    print(f"{Fore.MAGENTA}Queueing {post_len}")
    print()

    return media_list

def get_resolve_timelines(active_timeline_first=True):
    """ Return a list of all Resolve timeline objects in current project. """

    timelines = []

    timeline_len = project.GetTimelineCount()
    if timeline_len > 0:

        for i in range(1, timeline_len + 1):
            timeline = project.GetTimelineByIndex(i)
            timelines.append(timeline)

        if active_timeline_first:
            active = project.GetCurrentTimeline().GetName()                     # Get active timeline
            timeline_names = [x.GetName() for x in timelines]
            active_i = timeline_names.index(active)                             # It's already in the list, find it's index
            timelines.insert(0, timelines.pop(active_i))            # Move it to the front, indexing should be the same as name list
    else:
         return False

    return timelines

def search_and_link():
    """ Search through all existing media in active project and 
    attempt to find linkable proxies in expected directory
    """
    
    print("Not yet implemented!")
    print("Run the manual link program in 'Misc Tools' on the Streamdeck")
    sys.exit(1)
    

    linked = []
    # failed = []

    #TODO: Get this working. R

    timelines = get_resolve_timelines()
    if not timelines:
        raise Exception("No timelines exist in current project.")

    # Get clips from all timelines.
    for timeline in timelines:
        
        track_items = get_video_track_items(timeline)
        media_pool_items = get_media_pool_items(track_items)
        source_metadata = get_source_metadata(media_pool_items)
        source_metadata = remove_duplicate_elements(source_metadata)
        
    #     clips = timeline_data['clips']
    #     unlinked_source = [x for x in clips if x not in linked]

    #     if len(unlinked_source) == 0:
    #         if config['loglevel'] == "DEBUG": print(f"{Fore.YELLOW}No more clips to link in {timeline_data['name']}")
    #         continue
    #     else:
    #         print(f"{Fore.CYAN}Searching timeline {timeline_data['name']}")
        
    #     unlinked_proxies = [x for x in proxy_files if x not in linked]
    #     print(f"Unlinked source count: {len(unlinked_source)}")
    #     print(f"Unlinked proxies count: {len(unlinked_proxies)}")


    #     if len(unlinked_proxies) == 0:
    #         print(f"{Fore.YELLOW}No more proxies to link in {timeline_data['name']}")
    #         return
  
    #     linked_, failed_ = (__link_proxies(proxy_files, clips))

    #     linked.extend(linked_)
    #     failed.extend(failed_)

    #     if config['loglevel'] == "DEBUG": print(f"Linked: {linked}, Failed: {failed}")

    # if len(failed) > 0:
    #     print(f"{Fore.RED}The following files matched, but couldn't be linked. Suggest rerendering them:")
    #     [print(os.path.basename(x)) for x in failed]
    #     print()

    return linked

def legacy_link(media_list):
    """ This is sooooo dank. But it's the only way that works atm."""

    print(f"{Fore.CYAN}Linking {len(media_list)} proxies.")
    existing_proxies = []

    for media in media_list:
        proxy = media.get('Unlinked Proxy', None)
        if proxy == None:
            continue

        existing_proxies.append(proxy)

        if not os.path.exists(proxy):
            tkinter.messagebox.showerror(title = "Error linking proxy", message = f"Proxy media not found at '{proxy}'")
            print(f"{Fore.RED}Error linking proxy: Proxy media not found at '{proxy}'")
            continue

        else:
            media.update({'Unlinked Proxy': None}) # Set existing to none once linked

        media.update({'Proxy':"1280x720"})

        
    link_proxies(existing_proxies)    

    print()

    pre_len = len(media_list)
    media_list = [x for x in media_list if 'Unlinked Proxy' not in x]
    post_len = len(media_list)
    print(f"{pre_len - post_len} proxy(s) linked, will not be queued.")
    print(f"{Fore.MAGENTA}Queueing {post_len}")
    print()

    return media_list

def confirm(title, message):
    """General tkinter confirmation prompt using ok/cancel.
    Keeps things tidy"""

    answer = tkinter.messagebox.askokcancel(
        title = title, 
        message = message,
    )

    global some_action_taken
    some_action_taken = True
    return answer

def get_expected_proxy_path(media_list):
    """Retrieves the current expected proxy path using the source media path.
    """

    for media in media_list:

        file_path = media['File Path']
        p = pathlib.Path(file_path)

        # Tack the source media relative path onto the proxy media path
        expected_proxy_path = os.path.join(proxy_path_root, os.path.dirname(p.relative_to(*p.parts[:1])))
        media.update({'Expected Proxy Path': expected_proxy_path})

    return media_list

def handle_orphaned_proxies(media_list):
    """Prompts user to tidy orphaned proxies into the current proxy path structure.
    Orphans can become separated from a project if source media file-path structure changes.
    Saves unncessary re-rendering time and lost disk space."""

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
        
        print(f"{Fore.YELLOW}Orphaned proxies: {len(orphaned_proxies)}")
        answer = tkinter.messagebox.askyesnocancel(title="Orphaned proxies",
                                        message=f"{len(orphaned_proxies)} clip(s) have orphaned proxy media. " +
                                        "Would you like to attempt to automatically move these proxies to the up-to-date proxy folder?\n\n" +
                                        "For help, check 'Managing Proxies' in our YouTour documentation portal.")
        global some_action_taken
        some_action_taken = True
        
        if answer == True:
            print(f"{Fore.YELLOW}Moving orphaned proxies.")
            for proxy in orphaned_proxies:

                output_folder = os.path.dirname(proxy['New Path'])
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

                if os.path.exists(proxy['Old Path']):
                    shutil.move(proxy['Old Path'], proxy['New Path'])
                else:
                    print(f"{proxy['Old Path']} doesn't exist. Most likely a parent directory rename created this orphan.")
            print()


        elif answer == None:
            print("Exiting...")
            sys.exit(1)
    
    return media_list
    
def handle_already_linked(media_list):
    """Remove media from the queue if the source media already has a linked proxy that is online.
    As re-rendering linked clips is rarely desired behaviour, it makes sense to avoid clunky prompting.
    To re-render linked clips, simply unlink their proxies and try queueing proxies again. 
    You'll be prompted to handle offline proxies."""

    print(f"{Fore.CYAN}Checking for source media with linked proxies.")
    already_linked = [x for x in media_list if x['Proxy'] != "None"]

    if len(already_linked) > 0:
        
        print(f"{Fore.YELLOW}Skipping {len(already_linked)} already linked.")
        media_list = [x for x in media_list if x not in already_linked]
        print()

    return media_list

def handle_offline_proxies(media_list):

    print(f"{Fore.CYAN}Checking for offline proxies")
    offline_proxies = [x for x in media_list if x['Proxy'] == "Offline"]

    if len(offline_proxies) > 0:


        print(f"{Fore.CYAN}Offline proxies: {len(offline_proxies)}")
        answer = tkinter.messagebox.askyesnocancel(title="Offline proxies",
                                        message=f"{len(offline_proxies)} clip(s) have offline proxies.\n" +
                                        "Would you like to rerender them?")
        global some_action_taken
        some_action_taken = True


        if answer == True:
            print(f"{Fore.YELLOW}Rerendering offline: {len(offline_proxies)}")
            # Set all offline clips to None, so they'll rerender
            # [media['Proxy'] == "None" for media in media_list if media['Proxy'] == "Offline"]
            for media in media_list:
                if media['Proxy'] == "Offline":
                    media['Proxy'] = "None"
            print()


        if answer == None:
            print(f"{Fore.RED}Exiting...")
            sys.exit(0)
    
    return media_list

def handle_existing_unlinked(media_list):
    """Prompts user to either link or re-render proxy media that exists in the expected location, 
    but has either been unlinked at some point or was never linked after proxies finished rendering.
    Saves confusion and unncessary re-rendering time."""

    print(f"{Fore.CYAN}Checking for existing, unlinked media.")
    existing_unlinked = []

    
    get_expected_proxy_path(media_list)

    for media in media_list:
        if media['Proxy'] == "None":

            expected_proxy_path = media['Expected Proxy Path']
            media_basename = os.path.splitext(os.path.basename(media['File Name']))[0]
            expected_proxy_file = os.path.join(expected_proxy_path, media_basename)
            expected_proxy_file = os.path.splitext(expected_proxy_file)[0]
            
            existing = glob.glob(expected_proxy_file + "*.*")

            if len(existing) > 0:


                existing.sort(key=os.path.getmtime)
                if config['loglevel'] == "DEBUG": print(f"{Fore.MAGENTA} [x] Found {len(existing)} existing matches for {media['File Name']}")
                existing = existing[0]
                if config['loglevel'] == "DEBUG": print(f"{Fore.MAGENTA} [x] Using newest: '{existing}'")


                media.update({'Unlinked Proxy': existing})
                existing_unlinked.append(existing)


    if len(existing_unlinked) > 0:
        print(f"{Fore.YELLOW}Found {len(existing_unlinked)} unlinked")
        answer = tkinter.messagebox.askyesnocancel(title="Found unlinked proxy media",
                                        message=f"{len(existing_unlinked)} clip(s) have existing but unlinked proxy media. " +
                                        "Would you like to link them? If you select 'No' they will be re-rendered.")
        global some_action_taken
        some_action_taken = True

        if answer == True:
            media_list = legacy_link(media_list)
            
        
        elif answer == False:
            print(f"{Fore.YELLOW}Existing proxies will be OVERWRITTEN!")
            print()

        else:
            print("Exiting...")
            sys.exit(0)

    return media_list

def handle_workers():
    """Detect amount of online workers. Warn if none."""

    i = app.control.inspect().active_queues()

    if i is not None:
        # print(i)
        worker_count = len(i)

        if worker_count > 0:
            print(f"{Fore.CYAN}{worker_count} workers online")
            return

    else:
        print(f"{Fore.YELLOW}No workers online!")
        answer = tkinter.messagebox.askokcancel(title="No workers online",
                                        message=f"You haven't got any workers running!\n" +
                                                f"Don't forget to start one after queuing :) ")

        if answer is True:
            return

        else:
            print("Exiting...")
            sys.exit(0)

def handle_none_queuable(clips):
    """ Handle final queuing prompt. Warn and exit if nothing to queue,
    or confirm with count of queuable jobs."""

    if len(clips) == 0:

        global some_action_taken
        if not some_action_taken:
            
            print(f"{Fore.RED}No clips to queue.")
            tkinter.messagebox.showwarning("No new media to queue", "Looks like all your media is already linked. \n" +
                                           "If you want to re-rerender some proxies, unlink those existing proxies within Resolve and try again.")
            sys.exit(1)
        else:
            print(f"{Fore.GREEN}All clips linked now. No encoding necessary.")
            helpers.app_exit(0)

    # Final Prompt confirm
    if not confirm(
        "Go time!", 
        f"{len(clips)} clip(s) are ready to queue!\n" +
        "Continue?"
    ):
        sys.exit(0)
    return

def get_video_track_items(timeline):
    """ Get all video track items from the provided timeline """

    all_track_items = []

    # Get count of tracks (index) in active timeline
    track_len = timeline.GetTrackCount("video")       
    print(f"{Fore.GREEN}Video track count: {track_len}")

    # For each track in timeline (using index)
    for i in range(1, track_len + 1):

        # Get items
        track_items = timeline.GetItemListInTrack("video", i)
        
        if track_items is None:
            print(f"{Fore.YELLOW}No items found in track {i}")
            continue

        else:
            all_track_items.append(track_items)

    return all_track_items

def get_media_pool_items(track_items):
    """ Return media pool items for all track items """

    all_media_pool_items = []

    for track in track_items:
        for item in track:
            media_item = item.GetMediaPoolItem()
            all_media_pool_items.append(media_item)

    return all_media_pool_items

def get_source_metadata(media_pool_items):
    """ Return source metadata for each media pool item that passes criteria:

    - has file path (internally generated assets don't)
    - correct extension (BRAW loses its RAW and performs fine without proxies)
    - has linked media pool item (adjustment layers, nested timelines or offline footage don)

    """

    all_source_metadata = []

    for media_pool_item in media_pool_items:
        try:
            
            source_metadata = media_pool_item.GetClipProperty()

            source_ext = os.path.splitext(source_metadata['File Path'])[1].lower()
            if config['loglevel'] == "DEBUG": print(source_ext)

            if source_ext not in config['filters']['acceptable_exts']:
                if config['loglevel'] == "DEBUG": print(f"Ignoring unacceptable file type: '{source_metadata['File Path']}'")
                continue

            # Add the Resolve API media pool item object so we can call it directly to link
            # source_metadata.update({'media_pool_item_object':media_pool_item})
            all_source_metadata.append(source_metadata)

        except:
            if config['loglevel'] == "DEBUG": print(f"{Fore.MAGENTA}Skipping {media_pool_item.GetName()}, no linked media pool item.")    
            continue

    print(f"{Fore.GREEN}Total clips on timeline: {len(all_source_metadata)}")

    return all_source_metadata

def remove_duplicate_elements(elements):
    """ Ensure each element is unique so we don't process it multiple times."""

    unique_sets = set(frozenset(d.items()) for d in elements)
    unique_dict_list = [dict(s) for s in unique_sets]

    print(f"{Fore.GREEN}Unique: {len(unique_dict_list)}")

    return unique_dict_list

def wait_encode(job):
    """ Wait for job to finish, return statuses and notify user."""

    helpers.toast('Started encoding job')
    print(f"{Fore.YELLOW}Waiting for job to finish. Feel free to minimize.")
    
    job_metadata = job.join()

    # Notify failed
    if job.failed():
        fail_message = (
            "Some videos failed to encode!" + 
            f"Check flower dashboard at address: {config['celery_settings']['flower_url']}."
        )
        print(Fore.RED + fail_message)
        helpers.toast(fail_message)

    # Notify complete
    complete_message = f"Completed encoding {job.completed_count()} videos."
    print(Fore.GREEN + complete_message)
    print()

    helpers.toast(complete_message)

    return job_metadata

def main():
    """ Main function"""

    try:       

        print(f"{Fore.CYAN}Working on: {resolve_job_name}") 
        handle_workers()
        print()

        # Lets make it happen!
        track_items = get_video_track_items(timeline)
        media_pool_items = get_media_pool_items(track_items)
        source_metadata = get_source_metadata(media_pool_items)
        source_metadata = remove_duplicate_elements(source_metadata)

        print()

        clips = source_metadata

        # Prompt user for intervention if necessary
        clips = handle_already_linked(clips)
        clips = handle_offline_proxies(clips)
        clips = handle_existing_unlinked(clips)

        handle_none_queuable(clips)

        tasks = create_tasks(
            clips,
            project = project.GetName(), 
            timeline = timeline.GetName(),
        )

        job = queue_job(tasks)
        job_metadata = wait_encode(job)

        # ATTEMPT POST ENCODE LINK
        try:

            clips = legacy_link(clips)

        except:
            
            print(Fore.RED + "Couldn't link clips. Link manually...")
            helpers.app_exit(1, -1)

    
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        
        tkinter.messagebox.showerror("ERROR", tb)
        print("ERROR - " + str(e))

        helpers.app_exit(1)
        
if __name__ == "__main__":
    main()
