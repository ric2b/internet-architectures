import socket
import Pyro4

from chat_server import ServerAddress

Pyro4.config.SERIALIZERS_ACCEPTED = 'pickle'
Pyro4.config.SERIALIZER = 'pickle'


class Client:

    """
    Implements all the clients actions and monitors its state.
    """

    def __init__(self):
        self.id = None
        self.connection = None

    def register(self, server_uri):
        """
        Registers the client in the chat server with the given uri.

        :param server_uri: uri of the server to register to.
        """

        server = Pyro4.Proxy(server_uri)

        # call the register method of the server to obtain an id and the server's address
        response = server.register()
        self.id = response[0]
        server_address = ServerAddress(response[1], response[2])

        # establish a TCP connection with the server
        self.connection = socket.socket()
        self.connection.connect((server_address.ip_address, server_address.port))

        # register in the server by providing the client assigned id
        self.connection.send(self.id.hex.encode())

    def send_message(self, message: str):
        pass

    def recv_message(self) -> str:
        pass

    def __del__(self):
        if self.connection:
            self.connection.close()

client = Client()

# obtain the uri of the server
uri = input('What is the server uri?')

client.register(uri)
