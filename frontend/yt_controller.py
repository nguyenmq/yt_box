#-------------------------------------------------------------------------------
# Controller class for generating and parsing RPC messages
#-------------------------------------------------------------------------------

import json
import socket

from yt_rpc import yt_rpc

class yt_controller:

    def __init__(self, hostname):
        self._bufsz = 4096
        self._hostname = hostname

    def _send_data(self, msg):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self._hostname)
        sock.sendall(msg)
        return sock

    def _recv_data(self, sock):
        read = sock.recv(self._bufsz)
        data = ""
        while read and len(read) == self._bufsz:
            data += read.decode('utf-8')
            read = sock.recv(self._bufsz)

        if read:
            data += read.decode('utf-8')

        sock.close()

        return data

    def add_song(self, link):
        msg = {"cmd" : yt_rpc.CMD_REQ_ADD_VIDEO, "link" : link}
        json_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        sock = self._send_data(json_msg)

        new_queue = []
        data = self._recv_data(sock);
        if len(data) > 0:
            try:
                parsed_json = json.loads(data)
                for vid in parsed_json['videos']:
                    new_queue.append((vid['name'], vid['id']))
            except json.JSONDecodeError as e:
                print("Did not get a valid response")

        return new_queue

    def get_now_playing(self):
        msg = {"cmd" : yt_rpc.CMD_REQ_NOW_PLY}
        json_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        sock = self._send_data(json_msg)

        now_playing = ("None", "00")
        data = self._recv_data(sock)
        if data:
            try:
                parsed_json = json.loads(data)
                now_playing = (parsed_json['video']['name'], parsed_json['video']['id'])
            except json.JSONDecodeError as e:
                print("Did not get a valid response")

        return now_playing

    def get_queue(self):
        msg = {"cmd" : yt_rpc.CMD_REQ_QUEUE}
        json_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        sock = self._send_data(json_msg)

        q = []
        data = self._recv_data(sock)
        if data:
            try:
                parsed_json = json.loads(data)
                for vid in parsed_json['videos']:
                    q.append((vid['name'], vid['id']))
            except json.JSONDecodeError as e:
                print("Did not get a valid response")

        return q
