#!/usr/bin/env python3.6

import os
import shutil
import sys
from pathlib import Path
import webbrowser

import typer
import yaml


DEFAULT_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "default_settings.yml")
USER_SETTINGS_FILE = os.path.join(Path.home(), ".config","resolve_proxy_encoder", "user_settings.yml")


def get_defaults():
    """ Load default settings from yaml """

    with open(os.path.join(DEFAULT_SETTINGS_FILE)) as file: 
        return yaml.safe_load(file)

def check_settings():
    """ Check user settings exist """

    if not os.path.exists(USER_SETTINGS_FILE):

        if typer.confirm(
            f"No user settings found at path {USER_SETTINGS_FILE}\n" +
            "Load defaults now for adjustment?"
        ):

            # Create dir, copy file, open
            try:
                os.makedirs(os.path.dirname(USER_SETTINGS_FILE))
            except FileExistsError:
                typer.echo("Directory exists, skipping...")
            except OSError:
                typer.echo("Error creating directory!")
                sys.exit(1)

            shutil.copy(DEFAULT_SETTINGS_FILE, USER_SETTINGS_FILE)
            typer.echo(f"Copied default settings to {USER_SETTINGS_FILE}")
            typer.echo("Please customize as necessary.")
            webbrowser.open(USER_SETTINGS_FILE) # Technically unsupported method
            sys.exit(0)

        else:
            sys.exit(1)

def get_user_settings():
    """ Load user settings from yaml """

    with open(os.path.join(USER_SETTINGS_FILE)) as file: 
        return yaml.safe_load(file)

# Perform on import
check_settings()