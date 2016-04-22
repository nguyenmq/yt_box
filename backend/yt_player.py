import json
import subprocess
import threading
from collections import deque

from lib.yt_rpc import yt_rpc, vid_data

class yt_player:
    """
    Manages the video queue
    """

    def __init__(self, config):
        # Video queue and mutex

        scheduler = config.get_scheduler()
        self._scheduler = scheduler()
        self._qlock = threading.Lock()

        # Thread job queue and condition variable
        self._jobq = deque([])
        self._jobcv = threading.Condition()

        # Now playing title
        self._now_playing = None

        # Log video submissions
        self._log = open(file="submissions.md", mode="a", buffering=1)

        # callback table to handle rpc
        self._callbacks = {
            yt_rpc.CMD_REQ_ADD_VIDEO : self._hndlr_add_song,
            yt_rpc.CMD_REQ_NOW_PLY : self._hndlr_get_now_playing,
            yt_rpc.CMD_REQ_QUEUE : self._hndlr_get_queue
        }

        # spawn some threads
        for i in range(8):
            t = threading.Thread(target=self._thread_task)
            t.daemon = True
            t.start()

    def _thread_task(self):
        """
        Threading task. All requests are placed in the job queue where threads
        pull one off and process the command.
        """
        while True:
            self._jobcv.acquire()
            while len(self._jobq) == 0:
                self._jobcv.wait()
            sock, parsed_json = self._jobq.popleft()
            self._jobcv.release()

            self._callbacks[parsed_json['cmd']](sock, parsed_json)


    def _hndlr_add_song(self, sock, parsed_json):
        """
        Add a video to queue.

        :param parsed_json: Received json message
        :type parsed_json: parsed json object
        """
        link = parsed_json['link']

        returncode = 0

        try:
            output = subprocess.check_output( ["youtube-dl", "-e", "--get-id", link], universal_newlines=True )
        except subprocess.CalledProcessError as e:
            returncode = e.returncode
            output = e.output

        if returncode == 0:
            tokens = output.split('\n')
            new_video = vid_data(tokens[0], tokens[1], parsed_json['username'])
            self._qlock.acquire()
            self._scheduler.add_video(new_video)
            self._qlock.release()
            self._log.write("1. [{}](https://www.youtube.com/watch?v={}) - {}\n".format(new_video.name, new_video.id, new_video.username))
            self._log.flush()

        # TODO: return an error if url is malformed
        q = []
        for vid in self._scheduler.get_playlist():
            q.append({"name" : vid.name, "id" : vid.id, "username" : vid.username})
        msg = {"cmd" : yt_rpc.CMD_RSP_ADD_VIDEO, "videos" : q }
        sock.sendall(json.JSONEncoder().encode(msg).encode('utf-8'))

    def _hndlr_get_now_playing(self, sock, parsed_json):
        """
        Get the name and id of the video currently playing.

        :param parsed_json: Received json message
        :type parsed_json: parsed json object
        """
        if self._now_playing:
            video = { "name" : self._now_playing.name, "id" : self._now_playing.id, "username" : self._now_playing.username }
        else:
            video = { "name" : "None", "id" : 0, "username" : "None" }
        msg = {"cmd" : yt_rpc.CMD_RSP_NOW_PLY, "video" : video }
        sock.sendall(json.JSONEncoder().encode(msg).encode('utf-8'))

    def _hndlr_get_queue(self, sock, parsed_json):
        """
        Get the items in the queue

        :param parsed_json: Received json message
        :type parsed_json: parsed json object
        """
        q = []
        for vid in self._scheduler.get_playlist():
            q.append({"name" : vid.name, "id" : vid.id, "username" : vid.username})

        msg = {"cmd" : yt_rpc.CMD_RSP_QUEUE, "videos" : q }
        sock.sendall(json.JSONEncoder().encode(msg).encode('utf-8'))

    def get_next_video(self):
        """
        Pops the next item in the queue off and returns it. Or none if the
        queue is empty

        return: a tuple containing the video title and id
        """
        video = None
        self._qlock.acquire()
        video = self._scheduler.get_next_video()
        self._qlock.release()

        if video is None:
            self._now_playing = None
        else:
            self._now_playing = video

        return video

    def parse_msg(self, sock, msg):
        """
        Parses incoming RPC messages to verify there is a valid a command in
        the message and then appends the message to the job queue where it'll
        be handled by a thread in the pool.

        :param msg: Received message
        :type msg: string
        """
        try:
            parsed_json = json.loads(msg)
            if 'cmd' in parsed_json:
                if parsed_json['cmd'] in self._callbacks:
                    self._jobcv.acquire()
                    self._jobq.append((sock, parsed_json))
                    self._jobcv.notify()
                    self._jobcv.release()
                else:
                    print('No callback for "{}"'.format(parsed_json['cmd']))
            else:
                print('No command found in json message: {}'.format(parsed_json.dumps()))
        except json.JSONDecodeError as e:
            print(e)
            print( "json: {}".format(msg))

