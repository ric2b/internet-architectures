import socket

from circular_list import PacketId
from client_id import ClientId


class ClientInformation:

    """
    Holds all information that might be stored by the server for each client.
    This must be a class and not a namedtuple because they are immutable and the attributes
    can not be altered.
    """

    def __init__(self, client_id: ClientId, message_id: PacketId, connection: socket = None):
        self.client_id = client_id
        self.message_id = message_id
        self.connection = connection

    def __str__(self):
        return "Info(id=%s, packet_id=%s, %s)" % (self.client_id,
                                                  self.message_id,
                                                  "connected" if self.connection else "unconnected")
