""" All handlers prompt user for intervention. These handlers are specific to queuing and managing proxies. """


import glob
import os
import pathlib
import shutil
import sys
import tkinter
import tkinter.messagebox

import yaml
from colorama import Fore

# Get environment variables #########################################
script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "proxy_encoder", "config.yml")) as file: 
    config = yaml.safe_load(file)
    
acceptable_exts = config['filters']['acceptable_exts']
proxy_path_root = config['paths']['proxy_path_root']

debug = os.getenv('RPE_DEBUG')

#####################################################################


# Helpers


# Handlers

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
    '''Remove media from the queue if the source media already has a linked proxy that is online.
    As re-rendering linked clips is rarely desired behaviour, it makes sense to avoid clunky prompting.
    To re-render linked clips, simply unlink their proxies and try queueing proxies again. 
    You'll be prompted to handle offline proxies.'''

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
    '''Prompts user to either link or re-render proxy media that exists in the expected location, 
    but has either been unlinked at some point or was never linked after proxies finished rendering.
    Saves confusion and unncessary re-rendering time.'''

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
                if debug: print(f"{Fore.MAGENTA} [x] Found {len(existing)} existing matches for {media['File Name']}")
                existing = existing[0]
                if debug: print(f"{Fore.MAGENTA} [x] Using newest: '{existing}'")


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
