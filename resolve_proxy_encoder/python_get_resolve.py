#!/usr/bin/env python3.6

"""
This file serves to return a DaVinci Resolve object
"""
import imp
import sys
from rich import print as pprint
from resolve_proxy_encoder import helpers

def GetResolve():
    ext = ".so"
    if sys.platform.startswith("darwin"):
        path = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/"
    elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
        path = "C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\"
        ext = ".dll"
    elif sys.platform.startswith("linux"):
        path = "/opt/resolve/libs/Fusion/"
    else:
        raise Exception("Unsupported system! " + sys.platform)


    bmd = imp.load_dynamic("fusionscript", path + "fusionscript" + ext)
    resolve = bmd.scriptapp("Resolve")

    if resolve:
        sys.modules[__name__] = resolve
    else:
        pprint("[Red] :warning: Couldn't access the Resolve Python API. Is Resolve Open?[/]")
        helpers.app_exit(1, -1)

    return bmd.scriptapp("Resolve")