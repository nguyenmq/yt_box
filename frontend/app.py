#-------------------------------------------------------------------------------
# Main flask application
#-------------------------------------------------------------------------------

import subprocess
import threading
import copy

from collections import deque
from flask import Flask, render_template, request

class yt_queue:

    def __init__(self):
        self._q = deque([])
        self._cv = threading.Condition()
        self._now_playing = "None"
        self._log = open(file="submissions.txt", mode="a", buffering=1)

    def _get_yt_data( self, link ):
        title = None
        id = None
        complete = subprocess.run( ["youtube-dl", "-e", "--get-id", link], stdout=subprocess.PIPE, universal_newlines=True )

        if complete.returncode == 0:
            tokens = complete.stdout.split('\n')
            title = tokens[0]
            id = tokens[1]

        return title, id

    def add(self, link):
        name = "ERROR: Invalid link"
        queue = []

        link_info = self._get_yt_data( link )
        if link_info[0] != None:
            with self._cv:
                self._q.append(link_info)
                name = link_info[0]
                queue = copy.deepcopy(self._q)
                self._cv.notify_all()
            self._log.write("- {}\n    - https://www.youtube.com/watch?v={}\n".format(link_info[0], link_info[1]))
            self._log.flush()

        return name, queue

    def get_items(self):
        queue = []
        with self._cv:
            queue = copy.deepcopy(self._q)

        return queue

    def get_now_playing(self):
        return self._now_playing

    def wait_for_next_song(self):
        link_info = None

        with self._cv:
            while len(self._q) == 0:
                self._cv.wait()
            link_info = self._q.popleft()
            self._now_playing = copy.deepcopy(link_info[0])

        return link_info

    def close_log(self):
        self._log.close()

    def clear_now_play(self):
        self._now_playing = "None"

def task_yt_player():
    while True:
        link_info = yt_q.wait_for_next_song()

        if link_info != None:
            link = "https://www.youtube.com/watch?v={}".format( link_info[1] )
            subprocess.run( ["mpv", "--fs", link ] )
            yt_q.clear_now_play()


application = Flask(__name__)
yt_q = yt_queue()
thread_yt_player = threading.Thread( target=task_yt_player )
thread_yt_player.daemon = True
thread_yt_player.start()

@application.route('/')
def index():
    queue = yt_q.get_items()
    playing = yt_q.get_now_playing()
    return render_template('index.html', queue=queue, q_count=len(queue), playing=playing)

@application.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        name, queue = yt_q.add( request.form['link'])
        playing = yt_q.get_now_playing()
        return render_template( 'submit.html', link=name, queue=queue, q_count=len(queue), playing=playing )
    elif request.method == 'GET':
        queue = yt_q.get_items()
        playing = yt_q.get_now_playing()
        return render_template('index.html', queue=queue, q_count=len(queue), playing=playing)
    else:
        return "error"

if __name__ == '__main__':
    application.run( debug=True, host="0.0.0.0" )
    yt_q.close_log()
