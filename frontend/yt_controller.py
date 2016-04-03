#-------------------------------------------------------------------------------
# Controller class for generating and parsing RPC messages
#-------------------------------------------------------------------------------

import json
import socket

from yt_rpc import yt_rpc

class yt_controller:

    def __init__(self, hostname):
        # connection to yt_player
        self._con = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._con.connect(hostname)

    def __del__(self):
        if self._con:
            self._con.close()

    def add_song(self, link):
        msg = {"cmd" : yt_rpc.CMD_SUB_VIDEO, "link" : link}
        json_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        self._con.sendall(json_msg)
