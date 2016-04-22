import importlib
import sys

from configparser import ConfigParser

class yt_config:
    def __init__(self):
        config = ConfigParser()
        config.read("../config/yt_box.cfg")

        # Should check for any inappropriate types or missing values here and handle them appropriately

        # application setttings
        self.player = config.get('application', 'player', fallback='echo')
        self.player_args = config.get('application', 'player_args', fallback='{0}')
        self.player_enable = config.getboolean('application', 'player_enable', fallback=False)
        self._scheduler_path = config.get('application', 'scheduler', fallback='fifo.FIFOScheduler')
        self._extract_key(config)

        # connection settings
        self.host = config.get('connection', 'host', fallback='localhost')
        self.port = config.getint('connection', 'port')

    def get_scheduler(self):
        index = self._scheduler_path.rindex('.')
        module_path = self._scheduler_path[:index]
        class_name = self._scheduler_path[index + 1:]
        module = importlib.import_module('schedulers.' + module_path)
        return getattr(module, class_name, None)

    def _extract_key(self, config):
        filename = config.get('application', 'secret_key')

        if filename:
            try:
                key_file = open(filename, 'r')
                self.secret_key = key_file.read().strip('\n')
            except FileNotFoundError:
                print('Error: Secret key file "{}" not found'.format(filename))
                sys.exit()
