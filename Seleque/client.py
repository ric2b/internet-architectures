import socket
import Pyro4
from chat_server import Address
from circular_list import PacketId

name_server_uri = 'PYRO:name_server@localhost:60991'


class RegisterError(Exception):
    pass


class Client:

    """
    Implements all the clients actions and monitors its state.
    """

    def __init__(self):
        self.id = None
        self.current_packet = None
        self.room = None
        self.connection = None
        self.server = None

        self.name_server = Pyro4.Proxy(name_server_uri)

    def register(self, server_uri: Pyro4.URI, room: str, nickname: str, ):
        """
        Registers the client in the chat server with the given uri.

        :param server_uri: uri of the server to register to.
        :param room:
        :param nickname:
        :raises: ConnectionRefusedError: if was not able connect to the server.
        :raises: RegisterError: if the register process failed.
        """

        server = Pyro4.Proxy(server_uri)

        # call the register method of the server to obtain an id and the server's address
        client_id, server_address = server.request_id(nickname, room)

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

    def join_room(self, room: str, nickname: str):
        server_uri = self.name_server.join_room(room)
        self.server = Pyro4.Proxy(server_uri)

        self.register(server_uri, room, nickname)

        self.room = room

    def send_message(self, message):
        """
        Sends a message to all of the clients in the chat server.

        :param message: message to be sent.
        """

        self.server.send_message(self.id, message)

    def receive_message(self):
        """
        Receives a message from the chat server. If there is no message available, it
        blocks until a new message is available.

        :return: the received message.
        """

        self._wait_message()
        # read the message
        try:
            return self.server.receive_pending(self.room, self.current_packet)
        except EOFError:
            return None  # messages were already fetched
        except LookupError:
            raise NotImplementedError('Fetch from the beginning and warn the user')

    def _wait_message(self):
        """
        Blocks until a new message is ready to be received.
        """

        # wait for a signal from the server to unblock
        self.connection.recv(32)

    def __del__(self):
        if self.connection:
            self.connection.close()

if __name__ == "__main__":

    Pyro4.config.SERIALIZERS_ACCEPTED = 'pickle'
    Pyro4.config.SERIALIZER = 'pickle'

    import threading

    def input_loop(client_object):
        print('ready for input: ')
        try:
            while True:
                client_object.send_message(input())
        finally:
            print("".join(Pyro4.util.getPyroTraceback()))

try:
    client = Client()
    client.join_room(input('room: '), input('nickname: '))

    threading.Thread(None, input_loop, (), {client}).start()

    while True:
        print(client.receive_message())

finally:
    print("".join(Pyro4.util.getPyroTraceback()))
