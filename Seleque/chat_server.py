import socket
import uuid
from collections import namedtuple

import Pyro4
from circular_list import CircularList, PacketId

ServerAddress = namedtuple('ServerAddress', ['ip_address', 'port'])
ClientInformation = namedtuple('ClientInformation', ['id', 'packet_id', 'connection'])


class ChatServer:

    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        # each client is associated to the last message he read
        self.clients = {}
        # buffer with all the messages
        self.messages_buffer = CircularList(self.buffer_size)

        # create the listening socket #

        # create a socket to listen for new connections
        self.listen_socket = socket.socket()

        # DEBUG this function allows a port number to be used right after the
        # application terminates
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to the any interface and the port number 5000
        self.address = ServerAddress(socket.gethostname(), socket.htons(5000))
        self.listen_socket.bind((self.address.ip_address, self.address.port))

        # put the socket in listening mode
        self.listen_socket.listen(5)

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
