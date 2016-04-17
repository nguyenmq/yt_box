import datetime


class yt_rpc:

    """
    Defines constants used for parsing the RPC messages.
    """

    CMD_REQ_ADD_VIDEO = "CMD_REQ_ADD_VIDEO"
    CMD_REQ_REM_VIDEO = "CMD_REQ_REM_VIDEO"
    CMD_REQ_QUEUE = "CMD_REQ_QUEUE"
    CMD_REQ_NOW_PLY = "CMD_REQ_NOW_PLY"
    CMD_REQ_LOGIN_USER = "CMD_REQ_LOGIN_USER"
    CMD_REQ_LOGOUT_USER = "CMD_REQ_LOGOUT_USER"
    CMD_REQ_UPDT_NAME = "CMD_REQ_UPDT_NAME"

    CMD_RSP_ADD_VIDEO = "CMD_RSP_ADD_VIDEO"
    CMD_RSP_REM_VIDEO = "CMD_RSP_REM_VIDEO"
    CMD_RSP_QUEUE = "CMD_RSP_QUEUE"
    CMD_RSP_NOW_PLY = "CMD_RSP_NOW_PLY"
    CMD_RSP_LOGIN_USER = "CMD_RSP_LOGIN_USER"

    # alert types
    ALRT_SUCCESS = "success"
    ALRT_INFO    = "info"
    ALRT_WARNING = "warning"
    ALRT_DANGER  = "danger"

    def build_alert(alrt_type, alrt_emph="", alrt_msg=""):
        """
        Builds an alert dictionary to be used for an alert json object
        """
        return dict({"type" : alrt_type, "emph" : alrt_emph, "msg" : alrt_msg})

    def unpack_alert(alert):
        """
        Upacks the members of an alert dictionary and returns the members as a
        tuple
        """
        return (alert['type'], alert['emph'], alert['msg'])


class vid_data:

    """
    Represents the data for one video in the video queue
    """

    def __init__(self, name, vid_id, username, user_id):
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
        self.vid_id = vid_id
        self.username = username
        self.user_id = int(user_id)

class UserData:

    """
    Contains the data for a user
    """

    def __init__(self, user_id, username, logged_in, last_access):
        """
        Initialize the UserData object

        :param user_id: Id of the user
        :type user_id: integer

        :param username: Name of the user
        :type username: string

        :param logged_in: Whether user is logged in
        :type logged_in: boolean

        :param last_access: Date and time user last active
        :type last_access: string
        """
        self.user_id = int(user_id)
        self.username = username
        self.logged_in = bool(logged_in)
        self.last_access = datetime.datetime.strptime(last_access,
                                                      "%Y-%m-%d %H:%M:%S")
