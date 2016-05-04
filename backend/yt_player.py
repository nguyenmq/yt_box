import json
import subprocess
import threading
import sqlite3
import os.path

from collections import deque
from datetime import datetime, timedelta
from lib.yt_rpc import yt_rpc as yt_rpc
from lib.yt_rpc import vid_data, UserData


class yt_player:

    """
    Manages the video queue
    """

    class _DBInterface:

        """
        Managers the interface to the backend database
        """

        def __init__(self, config):
            """
            Initialize the user and submission database if it doesn't already
            exist
            """
            self._db_path = config.db_path
            if not os.path.isfile(self._db_path):
                with sqlite3.connect(self._db_path) as db:
                    db.executescript("""
                        CREATE TABLE users (
                            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE,
                            logged_in BOOLEAN NOT NULL,
                            last_access DATETIME NOT NULL);
                        CREATE INDEX usr_index ON users (
                            username);
                        CREATE TABLE submissions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            service TEXT NOT NULL,
                            vid_id TEXT NOT NULL,
                            date DATETIME NOT NULL,
                            user_id INTEGER NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(user_id));
                        CREATE TABLE settings (
                            user_id INTEGER NOT NULL,
                            setting TEXT NOT NULL,
                            value TEXT NOT NULL,
                            PRIMARY KEY (user_id, setting),
                            FOREIGN KEY (user_id) REFERENCES users(user_id));
                        """)
                    db.commit()

        def add_new_user(self, username):
            """
            Adds a new user to the database

            :param username: Name of user to add
            :type username: string

            :return: The id of the user added or 0 if something failed
            :type: integer
            """
            user_id = 0

            with sqlite3.connect(self._db_path) as db:
                cursor = db.cursor()
                args = (username,)
                try:
                    cursor.execute("""
                                   INSERT INTO users VALUES
                                   (NULL, ?, 1, datetime('now'));
                                   """,
                                   args)
                    db.commit()
                    # the last row id should be the id of the new user
                    user_id = cursor.lastrowid
                except sqlite3.IntegrityError:
                    user_id = 0

            return user_id

        def add_submission(self, vid_data):
            """
            Adds a new video submission to the submission databaes

            :param vid_data: The metadata for the video added
            :type user_id: vid_data class
            """
            with sqlite3.connect(self._db_path) as db:
                cursor = db.cursor()
                args = (vid_data.name,
                        "youtube",
                        vid_data.vid_id,
                        vid_data.user_id)
                cursor.execute("""
                               INSERT INTO submissions VALUES
                               (NULL, ?, ?, ?, datetime('now'), ?);
                               """,
                               args)
                db.commit()

        def check_user_exists(self, username):
            """
            Checks if the given username exists in the database

            :param username: username to check
            :type user_id: string

            :return: Wether the user exists in the database
            :type: boolean
            """
            exists = False
            with sqlite3.connect(self._db_path) as db:
                cursor = db.cursor()
                args = (username,)
                cursor.execute("""
                               SELECT COUNT(*) FROM users WHERE username = ?;
                               """,
                               args)
                count = cursor.fetchone()
                exists = count[0] > 0

            return exists

        def query_user_by_name(self, username):
            """
            Query for a user based on name. This works because the username
            field in the users database has only unique entries.

            :param username: Username to get user id of
            :type username: string

            :return: The data for the queried user or None
            :type: UserData object
            """
            user_data = None
            with sqlite3.connect(self._db_path) as db:
                cursor = db.cursor()
                args = (username,)
                cursor.execute("""
                               SELECT * FROM users WHERE username = ?;
                               """,
                               args)
                result = cursor.fetchone()
                if result is not None:
                    user_data = UserData(result[0],
                                         result[1],
                                         result[2],
                                         result[3])

            return user_data

        def query_user_by_id(self, user_id):
            """
            Query for a user based on user id.

            :param user_id: User id to query for
            :type user_id: integer

            :return: The data for the queried user or None
            :type: UserData object
            """
            if user_id is 0:
                return None

            user_data = None
            with sqlite3.connect(self._db_path) as db:
                cursor = db.cursor()
                args = (user_id,)
                cursor.execute("""
                               SELECT * FROM users WHERE user_id = ?;
                               """,
                               args)
                result = cursor.fetchone()
                if result is not None:
                    user_data = UserData(result[0],
                                         result[1],
                                         result[2],
                                         result[3])

            return user_data

        def query_username(self, user_id):
            """
            Queries for the username belonging to the passed in id

            :param user_id: User id to get username for
            :type user_id: int

            :return: The username of the user matching the given id or None if
                     not found
            :type: string
            """
            username = None
            with sqlite3.connect(self._db_path) as db:
                cursor = db.cursor()
                args = (user_id,)
                cursor.execute("""
                               SELECT username FROM users WHERE user_id = ?;
                               """,
                               args)
                result = cursor.fetchone()
                if result is not None:
                    username = result[0]

            return username

        def updt_user_login_status(self, user_id, status):
            """
            Marks the given user as logged in.

            :param user_id: The id of the user to log in
            :type user_id: integer

            :param status: The logged in status of the user
            :type status: boolean
            """
            with sqlite3.connect(self._db_path) as db:
                cursor = db.cursor()
                args = (int(status), user_id)
                if status:
                    # login
                    cursor.execute("""
                                   UPDATE users SET logged_in=?,
                                       last_access=datetime('now')
                                       WHERE user_id=?;
                                   """,
                                   args)
                else:
                    # logout
                    cursor.execute("""
                                   UPDATE users SET logged_in=?
                                       WHERE user_id=?;
                                   """,
                                   args)
                db.commit()

        def updt_username(self, user_id, username):
            """
            Updates the username belonging to the given user id.

            :param user_id: Id of the user
            :type user_id: string

            :param username: Name to change to
            :type username: string
            """
            with sqlite3.connect(self._db_path) as db:
                cursor = db.cursor()
                args = (username, user_id)
                cursor.execute("""
                               UPDATE users SET username=?
                                   WHERE user_id=?;
                               """,
                               args)
                db.commit()

    # ------------------------------------------------------
    # end of _DBInterface class
    # ------------------------------------------------------

    def __init__(self, config):
        """
        Initialize the yt_player class
        """
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
            yt_rpc.CMD_REQ_ADD_VIDEO:   self._hndlr_add_song,
            yt_rpc.CMD_REQ_REM_VIDEO:   self._hndlr_remove_song,
            yt_rpc.CMD_REQ_NOW_PLY:     self._hndlr_get_now_playing,
            yt_rpc.CMD_REQ_QUEUE:       self._hndlr_get_queue,
            yt_rpc.CMD_REQ_LOGIN_USER:  self._hndlr_login_user,
            yt_rpc.CMD_REQ_LOGOUT_USER: self._hndlr_logout_user,
            yt_rpc.CMD_REQ_UPDT_NAME:   self._hndlr_updt_username
        }

        self._db = self._DBInterface(config)

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

        :param sock: Socket message received over
        :type sock: socket class

        :param parsed_json: Received json message
        :type parsed_json: parsed json string
        """
        link = parsed_json['link']
        alrt_type = yt_rpc.ALRT_SUCCESS
        alrt_emph = ""
        alrt_msg = ""
        success = True
        returncode = 0

        try:
            output = subprocess.check_output(
                ["youtube-dl", "-e", "--get-id", link],
                universal_newlines=True)
        except subprocess.CalledProcessError as e:
            returncode = e.returncode
            output = e.output

        if returncode == 0:
            tokens = output.split('\n')
            username = self._db.query_username(parsed_json['user_id'])
            new_video = vid_data(tokens[0],
                                 tokens[1],
                                 username,
                                 parsed_json['user_id'])
            self._qlock.acquire()
            self._scheduler.add_video(new_video)
            self._qlock.release()
            self._log.write("1. [{}]({}{}) - {}\n"
                            .format("https://www.youtube.com/watch?v=",
                                    new_video.name,
                                    new_video.vid_id,
                                    new_video.username))
            self._log.flush()
            self._db.add_submission(new_video)
        else:
            alrt_type = yt_rpc.ALRT_DANGER
            alrt_emph = "Error"
            alrt_msg = "Could not find video for submitted link"
            success = False

        alert = yt_rpc.build_alert(alrt_type, alrt_emph, alrt_msg)
        msg = {"cmd":    yt_rpc.CMD_RSP_ADD_VIDEO,
               "status": success,
               "alert":  alert}
        self._send_response(sock, msg)

    def _hndlr_remove_song(self, sock, parsed_json):
        """
        Remove a video from the queue.

        :param sock: Socket message received over
        :type sock: socket class

        :param parsed_json: Received json message
        :type parsed_json: parsed json string
        """
        vid_id = parsed_json['vid_id']
        user_id = parsed_json['user_id']

        self._qlock.acquire()
        success = self._scheduler.remove_video(vid_id, user_id)
        self._qlock.release()

        alert = {}
        if success is False:
            alert = yt_rpc.build_alert(alrt_type=yt_rpc.ALRT_DANGER,
                                       alrt_emph="Error",
                                       alrt_msg="No video found with id: {}"
                                                .format(vid_id))
        else:
            alert = yt_rpc.build_alert(alrt_type=yt_rpc.ALRT_SUCCESS,
                                       alrt_emph="Success",
                                       alrt_msg="Video removed")

        msg = {"cmd":    yt_rpc.CMD_RSP_REM_VIDEO,
               "status": success,
               "alert":  alert}
        self._send_response(sock, msg)

    def _hndlr_logout_user(self, sock, parsed_json):
        """
        Handler for logging a user out of the session. Currently doesn't do
        anything.

        :param sock: Socket message received over
        :type sock: socket class

        :param parsed_json: Received json message
        :type parsed_json: parsed json string
        """
        self._db.updt_user_login_status(parsed_json['user_id'], True)

    def _hndlr_login_user(self, sock, parsed_json):
        """
        Handler for logging in a user. If the session contains a valid user id,
        then the user will be logged back in as that user. If the id is zero,
        then a new user will be created as long as the name is unique.

        :param sock: Socket message received over
        :type sock: socket class

        :param parsed_json: Received json message
        :type parsed_json: parsed json string
        """
        alrt_type = yt_rpc.ALRT_SUCCESS
        alrt_emph = ""
        alrt_msg = ""
        user_id = parsed_json['user_id']
        username = parsed_json['username']
        success = True

        user_data = self._db.query_user_by_name(username)

        if user_data is None:
            # Create a new user if name is unique
            user_id = self._db.add_new_user(username)
        elif user_data.logged_in is False:
            # Allow the name to be re-used
            username = user_data.username
            user_id = user_data.user_id
            self._db.updt_user_login_status(user_id, True)
        else:
            # Fill in the error
            alrt_type = yt_rpc.ALRT_DANGER
            alrt_emph = "Error"
            alrt_msg = '"{}" is already taken'.format(username)
            user_id = 0
            username = ""
            success = False

        alert = yt_rpc.build_alert(alrt_type, alrt_emph, alrt_msg)
        msg = {"cmd":      yt_rpc.CMD_RSP_LOGIN_USER,
               "user_id":  user_id,
               "username": username,
               "status":   success,
               "alert":    alert}
        self._send_response(sock, msg)

    def _hndlr_get_now_playing(self, sock, parsed_json):
        """
        Get the name and id of the video currently playing.

        :param sock: Socket message received over
        :type sock: socket class

        :param parsed_json: Received json message
        :type parsed_json: parsed json string
        """
        if self._now_playing:
            video = {"name":     self._now_playing.name,
                     "vid_id":   self._now_playing.vid_id,
                     "username": self._now_playing.username,
                     "user_id":  self._now_playing.user_id}
        else:
            video = {"name":     "Add Songs to the Queue",
                     "vid_id":   "0",
                     "username": "None",
                     "user_id":  0}
        msg = {"cmd": yt_rpc.CMD_RSP_NOW_PLY, "video": video}
        self._send_response(sock, msg)

    def _hndlr_get_queue(self, sock, parsed_json):
        """
        Get the items in the queue

        :param sock: Socket message received over
        :type sock: socket class

        :param parsed_json: Received json message
        :type parsed_json: parsed json string
        """
        q = []
        for vid in self._scheduler.get_playlist():
            q.append({"name":     vid.name,
                      "vid_id":   vid.vid_id,
                      "username": vid.username,
                      "user_id":  vid.user_id})

        msg = {"cmd": yt_rpc.CMD_RSP_QUEUE, "videos": q}
        self._send_response(sock, msg)

    def _hndlr_updt_username(self, sock, parsed_json):
        """
        Update the username of the user identified by given user id

        :param sock: Socket message received over
        :type sock: socket class

        :param parsed_json: Received json message
        :type parsed_json: parsed json string
        """
        alrt_type = yt_rpc.ALRT_SUCCESS
        alrt_emph = ""
        alrt_msg = ""
        user_id = parsed_json['user_id']
        username = parsed_json['username']
        success = True

        user_data = self._db.query_user_by_id(user_id)

        if user_data is None:
            # user id doesn't exist so return error
            success = False
            alrt_msg = 'User does not exist'
        elif username != user_data.username:
            # update the name only if it's unique
            existing = self._db.query_user_by_name(username)
            if existing is None:
                self._db.updt_username(user_id, username)
            else:
                success = False
                alrt_msg = '"{}" is already taken'.format(username)

        if success is False:
            alrt_type = yt_rpc.ALRT_DANGER
            alrt_emph = "Error"
            user_id = 0
            username = ""

        alert = yt_rpc.build_alert(alrt_type, alrt_emph, alrt_msg)
        msg = {"cmd":      yt_rpc.CMD_RSP_LOGIN_USER,
               "user_id":  user_id,
               "username": username,
               "status":   success,
               "alert":    alert}
        self._send_response(sock, msg)

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

    def _send_response(self, sock, msg):
        """
        Sends a response back over the RPC socket. Do note that the socket is
        closed by the select loop in main.

        :param sock: The socket to send the response over
        :type sock: socket class

        :param msg: Dictionary containing the json objects to send back. This
                    will be encoded to a proper json object.
        :type msg: dictionary
        """
        if len(msg) > 0 and sock.fileno() > -1:
            sock.sendall(json.JSONEncoder().encode(msg).encode('utf-8'))

    def _is_last_access_expired(self, user_data):
        """
        Check if the last_access time of the given user is older than the
        expiration timespan. Currently, a user can be automatically logged out
        if his/her last access time is greater than one day.

        :param user_data: User data of the user to check
        :type user_data: UserData

        :return: True if the last access time of the user has expired and False
                 otherwise.
        :type: boolean
        """
        expiration = timedelta(days=1)
        time_now = datetime.utcnow()
        return time_now - user_data.last_access > expiration

    def parse_msg(self, sock, msg):
        """
        Parses incoming RPC messages to verify there is a valid a command in
        the message and then appends the message to the job queue where it'll
        be handled by a thread in the pool.

        :param sock: Socket to respond to remote client on
        :type sock: socket object

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
                print('No command found in json message: {}'.format(
                    parsed_json.dumps()))
        except json.JSONDecodeError as e:
            print(e)
            print("json: {}".format(msg))
