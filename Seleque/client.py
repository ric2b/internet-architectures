import socket
import Pyro4

Pyro4.config.SERIALIZERS_ACCEPTED = 'pickle'
Pyro4.config.SERIALIZER = 'pickle'


class RegisterError(Exception):
    pass


class Client:

    """
    Implements all the clients actions and monitors its state.
    """

    def __init__(self):
        self.id = None
        self.connection = None
        self.server = None

    def register(self, server_uri):
        """
        Registers the client in the chat server with the given uri.

        :param server_uri: uri of the server to register to.
        :raises: ConnectionRefusedError: if was not able connect to the server.
        :raises: RegisterError: if the register process failed.
        """

        server = Pyro4.Proxy(server_uri)

        # call the register method of the server to obtain an id and the server's address
        client_id, server_address = server.request_id()

        # establish a TCP connection with the server
        connection = socket.socket()
        connection.connect((server_address.ip_address, server_address.port))

        # register in the server by providing the client assigned id
        connection.send(client_id.hex.encode())

        # wait for the server acknowledge
        ack = connection.recv(32).decode()

        if ack == "OK":
            self.id = client_id
            self.connection = connection
            self.server = server
        else:
            raise RegisterError("failed to register with the server")

    def send_message(self, message):
        """
        Sends a message to all of the clients in the chat server.

        :param message: message to be sent.
        """

        self.server.send_message(message)

    def receive_message(self):
        """
        Receives a message from the chat server. If there is no message available, it
        blocks until a new message is available.

        :return: the received message.
        """

        self._wait_message()
        # read the message
        return self.server.receive_pending(self.id)

    def _wait_message(self):
        """
        Blocks until a new message is ready to be received.
        """

        # wait for a signal from the server to unblock
        self.connection.recv(32)

    def __del__(self):
        if self.connection:
            self.connection.close()
