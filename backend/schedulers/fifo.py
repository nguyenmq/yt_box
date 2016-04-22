from collections import deque
from schedulers.scheduler_base import SchedulerBase


class FIFOScheduler(SchedulerBase):
    def __init__(self):
        self._q = deque([])

    def add_video(self, video):
        self._q.append(video)

    def get_playlist(self):
        return self._q

    def get_next_video(self):
        video = None

        if len(self._q) > 0:
            video = self._q.popleft()

        return video

