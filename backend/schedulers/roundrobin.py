import heapq
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
            if self.round > other.round:
                lt = True
            elif self.round == other.round and self.time > other.time:
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
        self._videos = []
        self._round = 0
        self._next_round = {}

    def add_video(self, video):
        """
        Add a video the queue

        :param video: Video to insert into queue
        :type video: vid_data
        """
        next_round = self._next_round.get(video.username, 0)

        # if they're new or haven't submitted in a while, give them priority
        if next_round < self._round:
            next_round = self._round

        rr_vid = self._RRVidData(video, next_round)
        heapq.heappush(self._videos, rr_vid)
        self._next_round[video.username] = next_round + 1

    def remove_video(self, id, username):
        """
        Remove the given video from the queue.

        :param id: ID of the video to remove
        :type id: string

        :param username: Name of user who submitted the video
        :type id: string

        :return: True if video was found and removed; False otherwise
        :type: boolean
        """
        rem_vid = None
        user_vids = []
        rm_round = 0

        for idx, rr_vid in enumerate(self._videos):
            if username == rr_vid.vid_data.username:
                if rr_vid.vid_data.id == id:
                    # Reduce the user's round number by one in order to keep the
                    # user's place in line
                    next_round = self._next_round.get(rr_vid.vid_data.username, 1)
                    self._next_round[rr_vid.vid_data.username] = next_round - 1
                    rem_vid = self._videos.pop(idx)
                    rm_round = rem_vid.round
                else:
                    # Keep track of the user's submittions so that they can be
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

            heapq.heapify(self._videos)
            return True

    def get_playlist(self):
        """
        Returns an ordered list of the videos in the queue

        :return: Ordered list of videos in the queue
        :type: [vid_data]
        """
        # TODO - traverse the actual tree
        ordered_list = list(self._videos)
        ordered_list.sort()
        vid_data = list(map(lambda video: video.vid_data, ordered_list))
        vid_data.reverse()
        return vid_data

    def get_next_video(self):
        """
        Pops off the next video in the queue and returns it.

        :return: The next video in the queue
        :type: vid_data
        """
        vid_data = None

        if len(self._videos) > 0:
            video = heapq.heappop(self._videos)
            self._round = video.round
            vid_data = video.vid_data

        return vid_data
