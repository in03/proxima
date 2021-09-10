""" Settings manager module.
"""
import configparser
import logging
import os

from typing import Union
from attrdict import AttrDict

from common import constants, helpers

# TODO: Debug logging is messy.
# There's probably a quicker way to ingest new settings.
# Consider iterating through settings by config 'section'
# or by ingest, since it's unlikely users will ingest conflicting values
# or if they do it will be on purpose.

# Change this to debug, info or warn (default)
# For debugging purposes
logging.basicConfig(level=logging.WARN)


class SettingsManager():
    """ Settings Manager takes multiple dictionary sources of application settings,
    finds their overriding preferences set in a central config file and returns them all
    as a dictionary or namespace / atrribute object.
    """

    def __init__(self, preference_directory, results_as_attr:bool=False):
        """ Create a new settings instance with a config preference file in the provided directory.
        Choose to return settings as a namespace object or dictionary with 'results_as_attr'.
        """

        # Get Logger
        self.logger = helpers.get_module_logger()

        # Return results as namespace / attributes?
        # Pass arg in class
        self.results_as_attr = results_as_attr

        # If no preference directory passed as arg, default to home
        if not preference_directory:
            self.conf_path = os.path.join(constants.LOCAL_STORAGE, "settings.ini")

        else:
            self.conf_path = preference_directory

        # Parent directory
        self.dirname = os.path.dirname(self.conf_path)

        # Init settings var
        self.settings = {}
        self.prefs = self._read_prefs()

        # Ensure settings directory exists
        if not os.path.exists(self.dirname):
            self.logger.warning("Settings folder is missing. Creating.")
            os.makedirs(self.dirname)

    def _read_prefs(self) -> dict:
        config = configparser.ConfigParser()
        config.read(self.conf_path)

        # Get dictionary of every item from every section
        prefs = {s:dict(config.items(s)) for s in config.sections()}

        self.logger.debug("Read config file: %s \nData: %s", self.conf_path, prefs)
        return prefs

    def update_settings(self, new_defaults:Union[None, dict]=None):

        prefs = self.prefs

        # FIXME: Forgot about the sections.
        # Temp rename to ease confusion, originally had pref_section as pref_key
        # Only worked because self.settings.update() was passed whole dict
        # Maybe better to match by key/val instead of sections?

        # Lol this is a bit silly, we only need one var
        # But I wrote them backwards
        if new_defaults is None:

            comp_a = prefs
            comp_b = self.settings

        else:

            comp_a = new_defaults
            comp_b = prefs

        # Iterate through all sections (full update)
        for section, keyval in comp_a.items():

            self.logger.debug("Section: %s", section)

            # If key matches, update setting
            if section in comp_b.keys():

                self.logger.info(
                    "Found matching section in config: '[%s]' Updating.",
                    section
                )

                self.settings.update({section: keyval})
                self._write_prefs()

                self.logger.debug(
                    "Pulling key-val '[%s]' from section %s in preferences.",
                    keyval, section
                )

    def _write_prefs(self):
        """ Rewrite updated preferences to file """

        try:

            # Convert dict to config
            parser = configparser.ConfigParser()
            parser.read_dict(self.settings)

            self.logger.debug("Attempting rewrite config file: %s", self.conf_path)

            # Rewrite config to file
            with open(self.conf_path, "w") as config_file:
                parser.write(config_file)

        except Exception as error:
            self.logger.error("Something went wrong! Couldn't write config file: %s", error)
            return False

        return True

    def _update_config(self, dict_source: dict) -> dict:
        """ Load an ini config file """

        conf_path = self.conf_path

        config = configparser.ConfigParser()

        # Write whole section if necessary
        for dict_sub in dict_source:

            # First element of outer dict should be 'Section'
            if isinstance(dict_sub, str):

                dict_section = str(dict_sub)
                config.add_section(dict_section)

                new_settings = {

                    k:v for (k,v) in dict_source[dict_section].items()
                    if k not in config[dict_section].keys()

                }


                logging.debug("New Settings: %s", new_settings)

                # TODO: Get this part to work!
                config[dict_section] = new_settings
                print(config)

        with open(conf_path, "a") as config_file:
            config.write(config_file)
        exit()

        self.logger.debug("Updated config %s", os.path.basename(self.conf_path))

        with open(conf_path, "r") as config_file:
            config.read(config_file)

        parsed_config = {s:dict(config.items(s)) for s in config.sections()}

        return parsed_config

    def _check_dict(self, dict_: dict) -> bool:
        """ Check dictionary meets criteria for source.
        Needs to be nested at least once, since we need sections and keys.
        """

        depth = helpers.get_dict_depth(dict_)
        self.logger.debug("Dict depth: %s", depth)

        if depth < 2:
            self.logger.warning(
                "Dictionary source: %s, is too shallow to contain section and key."
                "It will be ignored!", dict_
            )
            return False

        self.logger.debug("Registered dict source, %s", dict_)
        return True

    def get(self, section:Union[str, bool]=False) -> list:
        """ Return finalised preferences. Can return all, or just a section.
        Will return attributes instead of dict if set ony class init.
        """

        # Convert to namespace / attribute type
        if self.results_as_attr:
            results = AttrDict(**self.settings)

        # As plain dict
        results = self.settings

        # Section only
        if section:
            results = results.get(section, None)

        if results is None:
            self.logger.error("Invalid section: %s", section)
            return []

        return results

    def ingest(self, new_defaults: dict) -> Union[list, None]:
        """ Register provided settings. Any keys that don't exist in the config
        will have their defaults written.
        """

        self.logger.debug("Source provided: %s", new_defaults)

        # Check source is valid
        if not isinstance(new_defaults, dict):
            self.logger.warning("Invalid source type passed! Ignoring")
            return None

        if not self._check_dict(new_defaults):
            self.logger.warning("Invalid dict passed! Ignoring")
            return None

        # Merge current settings with new source
        self.settings = dict(**self.settings, **new_defaults)
        self.logger.debug("Self settings: %s", self.settings)

        # Add default settings to config if missing,
        # Pull preferred settings from config if present
        self.update_settings(new_defaults)

        # Get up to date preferences for all newly ingested
        prefs = [self.get(x) for x in new_defaults.keys()] 
        return prefs
