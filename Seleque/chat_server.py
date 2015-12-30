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
        id, reserve it, and return it to the client along with its address. This
        are required for a client to register to the server.

        :return: client id and the server's address.
        """

        # generate unique id for the new user
        client_id = uuid.uuid4()
        # register the client id but keep the client information empty
        # the client information will be stored after the clients registers
        self.clients[client_id] = None

    def send_message(self, message):
        """
        Sends a message to all the clients in the server. Puts the message in the
        message buffer and notifies all registered clients of the new message. If
        there any client with a broken connection they are removed.

        :param message: message to be sent.
        """

        self.messages_buffer.append(message)

        # notify all clients of a new message
        clients_to_remove = []
        for client in self.clients.values():
            try:
                client.connection.send("NEW MESSAGE".encode())
            except AttributeError:
                # the client is no completely registered yet
                # ignore this client and move to the next
                pass
            except BrokenPipeError:
                # this client has a broken connection
                client.connection.close()
                clients_to_remove.append(client.id)

        # remove the clients with broken connections
        for client_id in clients_to_remove:
            del self.clients[client_id]

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
