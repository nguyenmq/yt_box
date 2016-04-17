# -------------------------------------------------------------------------------
# Controller class for generating and parsing RPC messages
# -------------------------------------------------------------------------------

import json
import socket
import sys

sys.path.append("..")
from lib.yt_rpc import yt_rpc, vid_data


class yt_controller:

    def __init__(self, hostname, port):
        self._bufsz = 4096
        self._hostname = hostname
        self._port = port

    def _send_data(self, msg):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._hostname, self._port))
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

    def add_song(self, link, user_id):
        msg = {"cmd":     yt_rpc.CMD_REQ_ADD_VIDEO,
               "link":    link,
               "user_id": user_id}
        json_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        sock = self._send_data(json_msg)
        parsed_json = None
        data = self._recv_data(sock)

        if len(data) > 0:
            try:
                parsed_json = json.loads(data)
            except json.JSONDecodeError:
                print("Did not get a valid response")

        return parsed_json

    def remove_song(self, vid_id, user_id):
        """
        Interface to the CMD_REQ_REM_VIDEO rpc message.

        :param user_id: ID of the user
        :type user_id: integer
        """
        msg = {"cmd":     yt_rpc.CMD_REQ_REM_VIDEO,
               "vid_id":  vid_id,
               "user_id": int(user_id)}
        json_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        sock = self._send_data(json_msg)

        data = self._recv_data(sock)
        parsed_json = None

        if len(data) > 0:
            try:
                parsed_json = json.loads(data)
            except json.JSONDecodeError:
                print("Did not get a valid response")

        return parsed_json

    def login_user(self, user_id, username):
        msg = {"cmd":      yt_rpc.CMD_REQ_LOGIN_USER,
               "user_id":  user_id,
               "username": username}
        json_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        sock = self._send_data(json_msg)

        data = self._recv_data(sock)
        if len(data) > 0:
            try:
                parsed_json = json.loads(data)
            except json.JSONDecodeError:
                print("Did not get a valid response")

        return parsed_json

    def get_now_playing(self):
        msg = {"cmd": yt_rpc.CMD_REQ_NOW_PLY}
        json_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        sock = self._send_data(json_msg)

        now_playing = ("None", 0)
        data = self._recv_data(sock)
        if data:
            try:
                parsed_json = json.loads(data)
                now_playing = vid_data(parsed_json['video']['name'],
                                       parsed_json['video']['vid_id'],
                                       parsed_json['video']['username'],
                                       parsed_json['video']['user_id'])
            except json.JSONDecodeError:
                print("Did not get a valid response")

        return now_playing

    def get_queue(self):
        msg = {"cmd": yt_rpc.CMD_REQ_QUEUE}
        json_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        sock = self._send_data(json_msg)

        new_queue = []
        data = self._recv_data(sock)
        if data:
            try:
                parsed_json = json.loads(data)
                for vid in parsed_json['videos']:
                    new_video = vid_data(vid['name'], vid['vid_id'],
                                         vid['username'], vid['user_id'])
                    new_queue.append(new_video)
            except json.JSONDecodeError:
                print("Did not get a valid response")

        return new_queue
