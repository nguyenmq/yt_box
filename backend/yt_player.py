import json
import os
import select
import socket
import subprocess
import sys

from collections import deque

sys.path.append('../lib')
from yt_rpc import yt_rpc

class yt_player:
    """
    Manages the video queue
    """

    def __init__(self):
        self._q = deque([])
        self._now_playing = "None"
        #self._log = open(file="submissions.txt", mode="a", buffering=1)
        self._callbacks = {
            yt_rpc.CMD_SUB_VIDEO : self._enqueue
        }

    def _enqueue(self, parsed_json):
        link = parsed_json['link']
        complete = subprocess.run( ["youtube-dl", "-e", "--get-id", link], stdout=subprocess.PIPE, universal_newlines=True )
        if complete.returncode == 0:
            tokens = complete.stdout.split('\n')
            self._q.append(tokens)

        #for item in self._q:
        #    print( "{} = {}".format(item[0], item[1]))

    def parse_msg(self, msg):
        """
        Parses incoming RPC messages

        :param msg: Received message
        :type msg: string
        """
        response = None
        parsed_json = json.loads(msg)
        if 'cmd' in parsed_json:
            if parsed_json['cmd'] in self._callbacks:
                response = self._callbacks[parsed_json['cmd']](parsed_json)
            else:
                print('No callback for "{}"'.format(parsed_json['cmd']))
        else:
            print('No command found in json message: {}'.format(parsed_json.dumps()))

        return response
