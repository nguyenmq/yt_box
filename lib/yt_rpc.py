class yt_rpc:
    """
    Defines constants used for parsing the RPC messages.
    """

    CMD_REQ_ADD_VIDEO   = "CMD_REQ_ADD_VIDEO"
    CMD_REQ_REM_VIDEO   = "CMD_REQ_REM_VIDEO"
    CMD_REQ_QUEUE       = "CMD_REQ_QUEUE"
    CMD_REQ_NOW_PLY     = "CMD_REQ_NOW_PLY"
    CMD_REQ_ADD_USER    = "CMD_REQ_ADD_USER"
    CMD_RSP_ADD_VIDEO   = "CMD_RSP_ADD_VIDEO"
    CMD_RSP_REM_VIDEO   = "CMD_RSP_REM_VIDEO"
    CMD_RSP_QUEUE       = "CMD_RSP_QUEUE"
    CMD_RSP_NOW_PLY     = "CMD_RSP_NOW_PLY"

class vid_data:
    """
    Represents the data for one video in the video queue
    """

    def __init__(self, name, id, username):
        """
        Initialize the object

        :param name: Name of the video
        :type name: string

        :param id: youtube id of the video
        :type id: string

        :param username: Username of the submitter
        :type username: string
        """
        self.name = name
        self.id = id
        self.username = username

