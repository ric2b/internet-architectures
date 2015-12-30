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
        self.server = None

    def register(self, server_uri):
        """
        Registers the client in the chat server with the given uri.

        :param server_uri: uri of the server to register to.
        """

        self.server = Pyro4.Proxy(server_uri)

        # call the register method of the server to obtain an id and the server's address
        response = self.server.register()
        self.id = response[0]
        server_address = ServerAddress(response[1], response[2])

        # establish a TCP connection with the server
        self.connection = socket.socket()
        self.connection.connect((server_address.ip_address, server_address.port))

        # register in the server by providing the client assigned id
        self.connection.send(self.id.hex.encode())

        # wait for the server acknowledge
        ack = self.connection.recv(32).decode()
        if ack == "OK":
            print("register OK")
        else:
            print("register FAILED")

    def send_message(self, message):
        """
        Sends a message to all of the clients in the chat server.

        :param message: message to be sent.
        """

        self.server.send_message(message)

    def recv_message(self) -> str:
        """
        Receives a message from the chat server. If there is no message available, it
        blocks until a new message is available.

        :return: the received message.
        """
        message = self.connection.recv(1024).decode()
        print("%s: %s" % (self.id, message))

        # read the message
        return self.server.recv_message()

    def __del__(self):
        if self.connection:
            self.connection.close()

client = Client()

# obtain the uri of the server
uri = input('What is the server uri?')

client.register(uri)
client.send_message("ola bom dia")

while True:
    print(client.recv_message())
