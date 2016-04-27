import copy
from collections import deque
from schedulers.scheduler_base import SchedulerBase


class FIFOScheduler(SchedulerBase):
    """
    Implements a first-in-first-out style queueing system
    """

    def __init__(self):
        """
        Initializes the FIFOScheduler class
        """
        self._q = deque([])

    def add_video(self, video):
        """
        Append a video to the end of the queue

        :param video: Video to insert into queue
        :type video: vid_data
        """
        self._q.append(video)

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
        success = False

        for video in self._q:
            if video.id == id and video.username == username:
                rem_vid = video
                self._q.remove(video)
                success = True
                break

        return success

    def get_playlist(self):
        """
        Returns an ordered list of the videos in the queue

        :return: Ordered list of videos in the queue
        :type: [vid_data]
        """
        # I wish python made it eas to return an immutable
        # reference to this list
        return copy.copy(self._q)

    def get_next_video(self):
        """
        Pops off the next video in the queue and returns it.

        :return: The next video in the queue
        :type: vid_data
        """
        video = None

        if len(self._q) > 0:
            video = self._q.popleft()

        return video

