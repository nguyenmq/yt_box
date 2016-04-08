from configparser import ConfigParser

class yt_config:
    def __init__(self):
        config = ConfigParser()
        config.read('../config/yt_box.cfg')

        # Should check for any inappropriate types or missing values here and handle them appropriately

        # application setttings
        self.secret_key = config.get('application', 'secret_key')
        self.player = config.get('application', 'player', fallback='echo')
        self.player_args = config.get('application', 'player_args', fallback='{0}')

        # connection settings
        self.host = config.get('connection', 'host', fallback='localhost')
        self.port = config.getint('connection', 'port')



