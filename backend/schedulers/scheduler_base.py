class SchedulerBase:
    def add_video(self, video):
        raise NotImplementedError

    def get_playlist(self):
        raise NotImplementedError

    def get_next_video(self):
        raise NotImplementedError
