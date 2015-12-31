import socket
import threading
import uuid
from collections import namedtuple

import Pyro4
from circular_list import CircularList, PacketId

Address = namedtuple('Address', ['ip_address', 'port'])


class ClientInformation:

    """
    Holds all information that might be stored by the server for each client.
    This must be a class and not a namedtuple because they are immutable and the attributes
    can not be altered.
    """

    def __init__(self, id: int, message_id: PacketId, connection: socket = None):
        self.id = id
        self.message_id = message_id
        self.connection = connection

    def __str__(self):
        return "Info(id=%s, packet_id=%s, %s)" % (self.id,
                                                  self.message_id,
                                                  "connected" if self.connection else "unconnected")


class ChatServer:
    def __init__(self, address: Address, buffer_size):
        """
        Initializes the messages buffer. Creates an empty dictionary with all the
        mapping the clients ids to their information. Registers the server in the
        pyro daemon.

        :param address: the complete address for the server to bound to.
        :param buffer_size: the size of the message buffer.
        """

        self.address = address
        self.buffer_size = buffer_size

        # each client is associated to the last message he read
        self.clients = {}
        # buffer with all the messages
        self.messages_buffer = CircularList(self.buffer_size)

        # set pickle as the serializer used by pyro
        Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
        Pyro4.config.SERIALIZER = 'pickle'
        # register the server in the pyro daemon
        self.daemon = Pyro4.Daemon()
        self.uri = self.daemon.register(self, 'server')

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

        return client_id, self.address

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
        """
        Returns a list with all the messages in the message queue that the client
        has not received.

        :param client_id: id of the client requesting the messages.
        :return: list with the next messages in the message queue.
        """

        client_info = self.clients[client_id]
        current_index, message_list = self.messages_buffer.get_since(client_info.message_id)
        self.clients[client_id].message_id = current_index

        return message_list

    def start_loop(self):
        """
        Starts the chat server putting it in a loop waiting for new requests.
        """
        self.start_register()
        self.daemon.requestLoop()

    def start_register(self):
        threading.Thread(target=self._register).start()

    def _register(self):
        """
        Creates a listening socket bound the server address, to listen for new
        connections from clients that want to register in the server. When there
        is a new connection it tries to register the client.
        """

        # create a socket to listen for new connections
        listen_socket = socket.socket()

        # DEBUG this function allows a port number to be used right after the
        # application terminates
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to the any interface and the port number 5000
        listen_socket.bind((self.address.ip_address, self.address.port))

        # put the socket in listening mode
        listen_socket.listen(5)

        while True:
            # wait for a new connection
            connection, address = listen_socket.accept()

            # receive the client's id
            client_id = connection.recv(32)
            client_id = uuid.UUID(client_id.decode())

            try:
                self._register_client(client_id, connection)
            except KeyError:
                # there is no client with the provided id
                connection.send("ERROR".encode())
            else:
                # notify the client that the registration was successful
                connection.send("OK".encode())

    def _register_client(self, client_id, connection):

        # if the client_id does not exist then the registration is not valid
        if client_id not in self.clients:
            raise KeyError

        # a new user only receives messages that are sent after registering:
        # => the client must store the id of the current last message in the message buffer
        try:
            # get the last message id
            last_message_id = self.messages_buffer.get_newest()[0]
        except LookupError:
            # there was no messages in the message buffer yet
            # do not store any packet id
            last_message_id = None

        self.clients[client_id] = ClientInformation(id=client_id, message_id=last_message_id, connection=connection)