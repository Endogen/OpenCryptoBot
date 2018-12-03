import os
import json

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ConfigManager:

    _CFG_FILE = "config.json"
    _cfg = dict()

    def __init__(self, config_file=None):
        if config_file:
            ConfigManager._CFG_FILE = config_file

        ConfigManager._watch_changes()

    # Watch for config file changes
    @staticmethod
    def _watch_changes():
        observer = Observer()

        file = ConfigManager._CFG_FILE
        method = ConfigManager._read_cfg
        change_handler = ChangeHandler(file, method)

        observer.schedule(change_handler, ".", recursive=True)
        observer.start()

    @staticmethod
    def _read_cfg():
        if os.path.isfile(ConfigManager._CFG_FILE):
            with open(ConfigManager._CFG_FILE) as config_file:
                ConfigManager._cfg = json.load(config_file)
        else:
            cfg_file = ConfigManager._CFG_FILE
            exit(f"ERROR: No configuration file '{cfg_file}' found")

    @staticmethod
    def _write_cfg():
        if os.path.isfile(ConfigManager._CFG_FILE):
            with open(ConfigManager._CFG_FILE, "w") as config_file:
                json.dump(ConfigManager._cfg, config_file, indent=4)
        else:
            cfg_file = ConfigManager._CFG_FILE
            exit(f"ERROR: No configuration file '{cfg_file}' found")

    @staticmethod
    def get(*args):
        if not ConfigManager._cfg:
            ConfigManager._read_cfg()

        value = ConfigManager._cfg
        for key in args:
            value = value[key]

        return value if value is not None else None


class ChangeHandler(FileSystemEventHandler):
    file = None
    method = None

    def __init__(self, file, method):
        type(self).file = file
        type(self).method = method

    @staticmethod
    def on_modified(event):
        event_file = os.path.basename(event.src_path)
        config_file = os.path.basename(ChangeHandler.file)
        if event_file == config_file:
            ChangeHandler.method()
