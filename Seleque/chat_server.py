import socket
import uuid
from collections import namedtuple

import Pyro4
from circular_list import CircularList, PacketId

ServerAddress = namedtuple('ServerAddress', ['ip_address', 'port'])
ClientInformation = namedtuple('ClientInformation', ['id', 'packet_id', 'connection'])


class ChatServer:

    def __init__(self, address: ServerAddress, buffer_size):
        """
        Initializes the messages buffer. Creates an empty dictionary with all the
        mapping the clients ids to their information. Creates a listening socket
        bound to the given server address.

        :param address: the complete address for the server to bound to.
        :param buffer_size: the size of the message buffer.
        """

        self.address = address
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
        self.listen_socket.bind((self.address.ip_address, self.address.port))

        # put the socket in listening mode
        self.listen_socket.listen(5)

    def request_id(self):
        """
        Requests the server for a unique client id. The server will generate the
        id and return it to the client along with its address. The returned id
        and address are required for a client to register to the server.

        :return: client id and the server's address.
        """

        # generate unique id for the new user
        client_id = uuid.uuid4()

        # a new user only receives messages that are sent after he registers
        # then the user must store the id of the current last message

        try:
            self.clients[client_id] = ClientInformation(id=client_id,
                                                        last_message_id=self.messages_buffer.get_newest()[0])
        except AttributeError:
            # TODO change the raised exception to an LookupError
            # there was no messages in the message buffer yet
            # do not store any packet id
            self.clients[client_id] = ClientInformation(id=client_id)

        return client_id, self.address.ip_address, self.address.port

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
