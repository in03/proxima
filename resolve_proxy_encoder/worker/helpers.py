import platform
import subprocess

def check_wsl() -> bool:
    """ Return True if Python is running in WSL """

    if platform.system() == "Linux":
        return 'Microsoft' in platform.uname().release

    return False

def get_wsl_path(windows_path:str):
    """ Convert windows host paths to WSL paths if running WSL"""

    try:
        
        wsl_path = subprocess.run(['wslpath', windows_path], stdout=subprocess.PIPE).stdout.decode('utf-8')
        if not wsl_path or wsl_path == None:
            return windows_path

    except:
        return windows_path

    return wsl_path
