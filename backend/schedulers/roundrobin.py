import time
from schedulers.scheduler_base import SchedulerBase


class RoundRobin(SchedulerBase):
    """
    Implements a round-robin scheduling for ordering the videos in the queue.
    """

    class _RRVidData:
        """
        Internal round robin video data class
        """

        def __init__(self, video, round_):
            """
            Initializes the _RRVidData class
            """
            self.vid_data = video
            self.round = round_
            self.time = time.time()

        def __lt__(self, other):
            """
            Implements the less than operator
            """
            lt = False
            if self.round < other.round:
                lt = True
            elif self.round == other.round and self.time < other.time:
                lt = True

            return lt

        def shift_foward(self):
            """
            Move this video forward one round
            """
            self.round = self.round - 1

    def __init__(self):
        """
        Initializes the RoundRobin class
        """
        self._round = 0
        self._next_round = {}
        self._videos = []

    def add_video(self, video):
        """
        Add a video the queue

        :param video: Video to insert into queue
        :type video: vid_data
        """
        next_round = self._next_round.get(video.user_id, 0)

        # if they're new or haven't submitted in a while, give them priority
        if next_round < self._round:
            next_round = self._round

        rr_vid = self._RRVidData(video, next_round)
        self._videos.append(rr_vid)
        self._videos.sort()
        self._next_round[video.user_id] = next_round + 1

    def remove_video(self, vid_id, user_id):
        """
        Remove the given video from the queue.

        :param id: ID of the video to remove
        :type id: string

        :param user_id: ID of user who submitted the video
        :type id: integer

        :return: True if video was found and removed; False otherwise
        :type: boolean
        """
        rem_vid = None
        user_vids = []
        rm_round = 0

        for idx, rr_vid in enumerate(self._videos):
            if user_id == rr_vid.vid_data.user_id:
                if rr_vid.vid_data.vid_id == vid_id:
                    # Reduce the user's round number by one in order to keep
                    # the user's place in line
                    next_round = self._next_round.get(rr_vid.vid_data.username, 1)
                    self._next_round[rr_vid.vid_data.username] = next_round - 1
                    rem_vid = self._videos.pop(idx)
                    rm_round = rem_vid.round
                else:
                    # Keep track of the user's submissions so that they can be
                    # shifted one round forward
                    user_vids.append(rr_vid)

        if rem_vid is None:
            # This case shouldn't ever happen as long as the queue is
            # well-maintained
            return False
        else:
            # Shift the user's videos whose round were later than the removed
            # video foward one round
            for rr_vid in user_vids:
                if rr_vid.round > rm_round:
                    rr_vid.shift_foward()

            self._videos.sort()
            return True

    def get_playlist(self):
        """
        Returns an ordered list of the videos in the queue

        :return: Ordered list of videos in the queue
        :type: [vid_data]
        """
        playlist = []
        for video in self._videos:
            playlist.append(video.vid_data)

        return playlist

    def get_next_video(self):
        """
        Pops off the next video in the queue and returns it.

        :return: The next video in the queue
        :type: vid_data
        """
        vid_data = None

        if len(self._videos) > 0:
            video = self._videos.pop(0)
            self._round = video.round
            vid_data = video.vid_data

        return vid_data
