import os
import shutil
from pathlib import Path
from rich import print

settings_dir = Path(__file__).parent
default_settings_file = str(Path(settings_dir, "default_settings.toml").absolute())
user_settings_file = str(Path(settings_dir, "user_settings.toml"))
dotenv_settings_file = str(Path(settings_dir, ".env").absolute())

if not os.path.exists(user_settings_file):
    print("[magenta][Initialising 'user_settings.toml']")
    shutil.copy(default_settings_file, user_settings_file)
