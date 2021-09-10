""" Static application-wide variables exist here.
Some may be defined here, others may be system environment variables.
They should be all treated as immutable.
"""

import os
from pathlib import Path

APP_NAME = "Resolve Proxy Encoder"

HOME_PATH = str(Path.home())
PROJECT_PATH = Path(__file__).parents[1]
PROJECT_ROOT = os.path.basename(PROJECT_PATH)
LOCAL_STORAGE = os.path.join(HOME_PATH, "." + PROJECT_ROOT)
USER_PREFS_PATH = os.path.join(LOCAL_STORAGE, "preferences.ini")
