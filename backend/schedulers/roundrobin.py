import heapq
import time
from schedulers.scheduler_base import SchedulerBase


class _RRVidData:
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


class RoundRobin(SchedulerBase):
    def __init__(self):
        self._videos = []
        self._round = 0
        self._next_round = {}

    def add_video(self, vid_data):
        next_round = self._next_round.get(vid_data.username, 0)

        # if they're new or haven't submitted in a while, give them priority
        if next_round < self._round:
            next_round = self._round
        video = _RRVidData(vid_data, next_round)
        heapq.heappush(self._videos, video)

        self._next_round[vid_data.username] = next_round + 1

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
