import socket
import uuid
import Pyro4
from circular_list import CircularList, PacketId


class ClientInformation:

    """ Holds all information that might be stored by the server for each client """

    def __init__(self, id: int, last_packetid: PacketId, connection: socket = None):
        self.id = id
        self.last_packetid = last_packetid
        self.connection = connection

    def __str__(self):
        return "Info(id=%s, packet_id=%s, %s)" % (self.id,
                                                  self.last_packetid,
                                                  "connected" if self.connection else "unconnected")


class ChatServer:

    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        # each client is associated to the last message he read
        self.clients = {}
        # buffer with all the messages
        self.messages_buffer = CircularList(self.buffer_size)

    def register(self):
        # generate unique id for the new user
        client_id = uuid.uuid4()

        # a new user only receives messages that are sent after he registers
        # assign to the user the index of the last message

        try:
            self.clients[client_id] = self.messages_buffer.get_newest()[0]
        except AttributeError:
            self.clients[client_id] = None

        return client_id

    def send_message(self, message):
        self.messages_buffer.append(message)

    def receive_pending(self, client_id):

        current_index, message_list = self.messages_buffer.get_since(self.clients[client_id])
        self.clients[client_id] = current_index

        return message_list


if __name__ == "__main__":

    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
    Pyro4.config.SERIALIZER = 'pickle'

    daemon = Pyro4.Daemon()
    uri = daemon.register(ChatServer(4), 'server')
    print("Ready. Object uri =", uri)
    daemon.requestLoop()
