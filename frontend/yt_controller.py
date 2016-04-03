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
        msg = {"cmd" : yt_rpc.CMD_REQ_ADD_VIDEO, "link" : link}
        json_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        self._con.sendall(json_msg)

    def get_now_playing(self):
        msg = {"cmd" : yt_rpc.CMD_REQ_NOW_PLY}
        json_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        self._con.sendall(json_msg)

        now_playing = ("None", "00")
        data = self._con.recv(1024)
        if data:
            try:
                parsed_json = json.loads(data.decode('utf-8'))
                now_playing = (parsed_json['video']['name'], parsed_json['video']['id'])
            except:
                print("Did not get a valid response")

        return now_playing

    def get_queue(self):
        msg = {"cmd" : yt_rpc.CMD_REQ_QUEUE}
        json_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        self._con.sendall(json_msg)

        q = []
        data = self._con.recv(2048)
        if data:
            try:
                parsed_json = json.loads(data.decode('utf-8'))
                for vid in parsed_json['videos']:
                    q.append((vid['name'], vid['id']))
            except:
                print("Did not get a valid response")

        return q
