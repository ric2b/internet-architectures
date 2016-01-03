class ClientInformation:

    """
    Holds all information that might be stored by the server for each client.
    This must be a class and not a namedtuple because they are immutable and the attributes
    can not be altered.
    """

    def __init__(self, client_id, message_id, client, nickname: str = None):
        self.client_id = client_id
        self.nickname = nickname
        self.message_id = message_id
        self.client = client

    def __str__(self):
        return "Info(id=%s: %s)" % (self.nickname, "connected" if self.connection else "unconnected")


