import json
import subprocess
import sys
import threading

from collections import deque

sys.path.append('../lib')
from yt_rpc import yt_rpc

class yt_player:
    """
    Manages the video queue
    """

    def __init__(self):
        # Video queue and mutex
        self._q = deque([])
        self._qlock = threading.Lock()

        # Thread job queue and condition variable
        self._jobq = deque([])
        self._jobcv = threading.Condition()

        # Now playing title
        self._now_playing = "None"

        # Log video submissions
        # self._log = open(file="submissions.txt", mode="a", buffering=1)

        # callback table to handle rpc
        self._callbacks = {
            yt_rpc.CMD_SUB_VIDEO : self._enqueue
        }

        # spawn some threads
        for i in range(5):
            t = threading.Thread(target=self._thread_task)
            t.daemon = True
            t.start()

    def _thread_task(self):
        """
        Threading task. Requesting the video name and id can take a while so the
        job is offloaded to a thread. A submitted video link is added to a job
        queue. A thread will wait on a condition variable to pull a link from
        the job queue. Once a link is pulled from the job queue, it will request
        the metadata and then do an atomic add to the video queue.
        """
        while True:
            self._jobcv.acquire()
            while len(self._jobq) == 0:
                self._jobcv.wait()
            link = self._jobq.popleft()
            self._jobcv.release()

            complete = subprocess.run( ["youtube-dl", "-e", "--get-id", link], stdout=subprocess.PIPE, universal_newlines=True )
            if complete.returncode == 0:
                tokens = complete.stdout.split('\n')
                self._qlock.acquire()
                self._q.append(tokens)
                #print("start")
                #for item in self._q:
                #    print("{} = {}".format(item[0], item[1]))
                self._qlock.release()

    def _enqueue(self, parsed_json):
        """
        Add a video. This will first add the link to the thread job queue where
        a thread will do the work of requesting video metatadata and then adding
        that data to the true video queue.

        :param parsed_json: Received json message
        :type parsed_json: parsed json object
        """
        link = parsed_json['link']
        self._jobcv.acquire()
        self._jobq.append(link)
        self._jobcv.notify()
        self._jobcv.release()

        return None

    def get_next_video(self):
        """
        Pops the next item in the queue off and returns it. Or none if the
        queue is empty

        return: a tuple containing the video title and id
        """
        video = None
        self._qlock.acquire()
        if len(self._q) > 0:
            video = self._q.popleft()
        self._qlock.release()

        if video is None:
            self._now_playing = "None"
        else:
            self._now_playing = video[0]

        return video

    def parse_msg(self, msg):
        """
        Parses incoming RPC messages and passes the command to the relevant
        callback handler.

        :param msg: Received message
        :type msg: string
        """
        response = None

        try:
            parsed_json = json.loads(msg)
            if 'cmd' in parsed_json:
                if parsed_json['cmd'] in self._callbacks:
                    response = self._callbacks[parsed_json['cmd']](parsed_json)
                else:
                    print('No callback for "{}"'.format(parsed_json['cmd']))
            else:
                print('No command found in json message: {}'.format(parsed_json.dumps()))
        except:
            print( "Invalid json string given: {}".format(msg))

        return response

