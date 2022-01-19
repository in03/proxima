#!/usr/bin/env python3.6

import os
import shutil
import webbrowser
from pathlib import Path

import typer
from attrdict import AttrDict
from resolve_proxy_encoder.helpers import (
    app_exit,
    get_rich_logger,
    install_rich_tracebacks,
)
from ruamel.yaml import YAML

from schema import SchemaError

from .schema import settings_schema

# # Hardcoded because we haven't loaded user settings yet
logger = get_rich_logger("WARNING")
install_rich_tracebacks()

DEFAULT_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "default_settings.yml")
USER_SETTINGS_FILE = os.path.join(
    Path.home(), ".config", "resolve_proxy_encoder", "user_settings.yml"
)


class Settings:
    def __init__(
        self,
        default_settings_file=DEFAULT_SETTINGS_FILE,
        user_settings_file=USER_SETTINGS_FILE,
    ):

        self.yaml = YAML()
        self.default_file = default_settings_file
        self.user_file = user_settings_file

        self.default_settings = self._get_default_settings()
        self.user_settings = self._get_user_settings()

        self._ensure_file()
        # self._ensure_keys()
        self._validate_schema()

    def _get_default_settings(self):
        """Load default settings from yaml"""

        logger.debug(f"Loading default settings from {self.default_file}")

        with open(os.path.join(self.default_file)) as file:
            return self.yaml.load(file)

    def _get_user_settings(self):
        """Load user settings from yaml"""

        logger.debug(f"Loading user settings from {self.user_file}")

        with open(self.user_file, "r") as file:
            return self.yaml.load(file)

    def _ensure_file(self):
        """Copy default settings to user settings if it doesn't exist

        Prompt the user to edit the file afterwards, then exit.
        """

        logger.debug(f"Ensuring settings file exists at {self.user_file}")

        if not os.path.exists(self.user_file):

            if typer.confirm(
                f"No user settings found at path {self.user_file}\n"
                + "Load defaults now for adjustment?"
            ):

                # Create dir, copy file, open
                try:
                    os.makedirs(os.path.dirname(self.user_file))
                except FileExistsError:
                    typer.echo("Directory exists, skipping...")
                except OSError:
                    typer.echo("Error creating directory!")
                    app_exit(1)

                shutil.copy(self.default_file, self.user_file)
                typer.echo(f"Copied default settings to {self.user_file}")
                typer.echo("Please customize as necessary.")
                webbrowser.open(self.user_file)  # Technically unsupported method

            app_exit(0)

    def _ensure_keys(self):
        """Copy defaults for any missing keys if they don't exist"""

        logger.debug(f"Ensuring all settings keys exist in {self.user_file}")

        # Add missing keys

        # TODO: This won't work how I want it to...
        # I need to insert the missing keys into the user settings file
        # WHERE THEY ARE MISSING. This will append them to the end.
        # Instead, load the user settings to dict, write default to file,
        # update the defaults with the user values.
        # Warn on missing keys

        with open(self.user_file, "r+") as file_:
            user_settings = self.yaml.load(file_)

            needs_write = False
            for key, value in self.default_settings.items():

                print(key)
                if key not in user_settings:

                    logger.warning(
                        f"Adding missing key '{key}' to user settings with value '{value}'"
                    )
                    user_settings[key] = value

                self.yaml.dump(user_settings, file_)

        # Warn unsupported keys
        for key in user_settings:
            if key not in self.default_settings:
                logger.warning(f"Found unused key '{key}' in user settings")

    def _validate_schema(self):
        """Validate user settings against schema"""

        logger.debug(f"Validating user settings against schema")

        try:

            settings_schema.validate(self.user_settings)

        except SchemaError as e:

            logger.error(f"Error validating settings: {e}")
            app_exit(1)

        logger.info("Settings validated successfully")
