class SchedulerBase:
    """
    A base class for which all video queue schedulers must inherit. A scheduler
    maintains an ordering of the queue based on some metric it implements.
    """

    def add_video(self, video):
        """
        Interface for adding a new video to the scheduler's queue

        :param video: Video to insert into queue
        :type video: vid_data
        """
        raise NotImplementedError

    def get_next_video(self):
        """
        Interface for getting the next video in the scheduler's queue.

        :return: The next video in the queue
        :type: vid_data
        """
        raise NotImplementedError

    def get_playlist(self):
        """
        Interface for getting a list of the videos in the scheduler's queue.

        :return: Ordered list of videos in the queue
        :type: [vid_data]
        """
        raise NotImplementedError

    def remove_video(self, vid_id, user_id):
        """
        Interface for removing a video from the scheduler's queue. The removed
        video will match the given id and username.

        :param id: ID of the video to remove
        :type id: string

        :param username: Name of user who submitted the video
        :type id: string

        :return: True if video was found and removed; False otherwise
        :type: boolean
        """
        raise NotImplementedError
