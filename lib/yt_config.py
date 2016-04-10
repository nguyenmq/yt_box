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
        self._extract_key(config)

        # connection settings
        self.host = config.get('connection', 'host', fallback='localhost')
        self.port = config.getint('connection', 'port')


    def _extract_key(self, config):
        filename = config.get('application', 'secret_key')

        if filename:
            try:
                key_file = open(filename, 'r')
                self.secret_key = key_file.read().strip('\n')
            except FileNotFoundError:
                print('Error: Secret key file "{}" not found'.format(filename))
                sys.exit()
