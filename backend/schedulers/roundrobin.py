import heapq
import time
from schedulers.scheduler_base import SchedulerBase


class RoundRobin(SchedulerBase):

    class _RRVidData:
        """
        Internal round robin video data class
        """
        def __init__(self, video, round_):
            self.vid_data = video
            self.round = round_
            self.time = time.time()

        def __lt__(self, other):
            lt = False
            if self.round > other.round:
                lt = True
            elif self.round == other.round and self.time > other.time:
                lt = True

            return lt

        def shift_foward(self):
            self.round = self.round - 1

    def __init__(self):
        self._videos = []
        self._round = 0
        self._next_round = {}

    def add_video(self, vid_data):
        next_round = self._next_round.get(vid_data.username, 0)

        # if they're new or haven't submitted in a while, give them priority
        if next_round < self._round:
            next_round = self._round

        video = self._RRVidData(vid_data, next_round)
        heapq.heappush(self._videos, video)
        self._next_round[vid_data.username] = next_round + 1

    def remove_video(self, id, username):
        rem_vid = None
        user_vids = []

        for idx, rr_vid in enumerate(self._videos):
            if username == rr_vid.vid_data.username:
                if rr_vid.vid_data.id == id:
                    # Reduce the user's round number by one in order to keep the
                    # user's place in line
                    next_round = self._next_round.get(rr_vid.vid_data.username, 1)
                    self._next_round[rr_vid.vid_data.username] = next_round - 1
                    rem_vid = self._videos.pop(idx)
                else:
                    # Keep track of the user's submittions so that they can be
                    # shifted one round forward
                    user_vids.append(rr_vid)

        if rem_vid is None:
            # This case shouldn't ever happen as long as the queue is
            # well-maintained
            print("RR: Didn't find {} in queue...\n".format(id))
            return False
        else:
            for rr_vid in user_vids:
                rr_vid.shift_foward()

            heapq.heapify(self._videos)
            return True

    def get_playlist(self):
        # TODO - traverse the actual tree
        ordered_list = list(self._videos)
        ordered_list.sort()
        vid_data = list(map(lambda video: video.vid_data, ordered_list))
        vid_data.reverse()
        return vid_data

    def get_next_video(self):
        vid_data = None

        if len(self._videos) > 0:
            video = heapq.heappop(self._videos)
            self._round = video.round
            vid_data = video.vid_data

        return vid_data
