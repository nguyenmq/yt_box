from collections import deque
from schedulers.scheduler_base import SchedulerBase


class FIFOScheduler(SchedulerBase):
    def __init__(self):
        self._q = deque([])

    def add_video(self, video):
        self._q.append(video)

    def remove_video(self, id):
        rem_vid = None
        for video in self._q:
            if video.id == id:
                print("Q: Found {}, removing...\n".format(id))
                rem_vid = video
                self._q.remove(video)
                break
        else:
            print("Q: Didn't find {} in queue...\n".format(id))
        return rem_vid

    def get_playlist(self):
        return self._q

    def get_next_video(self):
        video = None

        if len(self._q) > 0:
            video = self._q.popleft()

        return video

