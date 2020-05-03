from __future__ import annotations

import logging
import os

from configuration.model import Config


class ConfigurationManager(object):
    """Manages loading and saving the project's configuration.

    This class has a shared global instance that can be used across the
    application. It is accessible through the `instance()` method
    """
    __instance: ConfigurationManager = None
    THIS_DIRECTORY = os.path.dirname(__file__)
    PROJECT_DIRECTORY = os.path.dirname(THIS_DIRECTORY)
    CONFIG_FILE = os.path.abspath(os.path.join(PROJECT_DIRECTORY, "config.json"))

    @classmethod
    def instance(cls):
        return cls.__instance

    @classmethod
    def config(cls):
        return cls.__instance.config

    @classmethod
    def initialize(cls, events, path=CONFIG_FILE):
        log = logging.getLogger(cls.__name__)
        cls.__instance = ConfigurationManager(path)
        try:
            cls.__instance.load()
        except FileNotFoundError:
            # Not considered an error we should alert on.
            log.info("No config file. Using defaults")
        except Exception as e:
            log.error("Error loading config file: %s. Using defaults", e)
            from data.alerts import AlertCodes
            events.alerts_queue.enqueue_alert(AlertCodes.INVALID_CONFIGURATION_FILE)
        finally:
            # We want to save even on successful load because the existing file
            # might be valid JSON but incomplete, E.g in case of version upgrade.
            cls.__instance.save()
        return cls.__instance

    def __init__(self, path):
        self._path = path
        self._log = logging.getLogger(self.__class__.__name__)
        self.config = Config()

    def load(self):
        self.config = Config.parse_file(self._path)
        self._log.info("Configuration loaded from %s", self._path)

    def save(self):
        try:
            with open(self._path, "w") as f:
                f.write(self.config.json(indent=2))
                f.flush()
                os.fsync(f.fileno())
            self._log.info(f"Configuration saved to %s", self._path)
        except Exception as e:
            # There's nothing more we can do about it.
            self._log.error("Error saving configuration: %s", e)
