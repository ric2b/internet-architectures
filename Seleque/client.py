import Pyro4

from chat_server import ChatServer
from name_server import NameServer, InvalidIdError
from room_id import RoomId

name_server_uri = 'PYRO:name_server@localhost:63669'


class RegisterError(Exception):
    pass


class Client:

    """
    Implements all the clients actions and monitors its state.
    """

    def __init__(self):
        self.id = None
        self.room = None
        self.server = None
        self.name_server = Pyro4.Proxy(name_server_uri) # type: NameServer

        # pyro daemon for the client
        # this must be stored to enable a clean shutdown of the client
        self.daemon = Pyro4.Daemon()
        self.client_uri = None

    def _join_room(self, room_id: RoomId, nickname: str):
        """
        Joins a room with the given nickname.

        :param room_id: id of the room to register to.
        :param nickname: nickname to assign the client.
        """
        joined_successfully = False
        while not joined_successfully:
            # requests a server URI and a client id from the name server
            self.id, server_uri = self.name_server.join_room(room_id)

            # generate the client's uri from the client id in order to be unique
            self.client_uri = self.daemon.register(self, str(self.id))
            # initialize the pyro service for the client
            threading.Thread(target=self.daemon.requestLoop).start()

            # get the server where from the server uri
            self.server = Pyro4.Proxy(server_uri)  # type: ChatServer
            try:
                # register the client in the server
                self.server.register(room_id, self.id, self.client_uri, nickname)
            except InvalidIdError:
                # retry to register
                continue
            else:
                joined_successfully = True

    def send_message(self, message):
        """
        Sends a message to all of the clients in the chat server.

        :param message: message to be sent.
        """

        self.server.send_message(self.room, self.id, message)

    def receive_message(self):
        """
        Receives a message from the chat server. If there is no message available, it
        blocks until a new message is available.

        :return: the received message.
        """

        self._wait_message()
        # read the message
        try:
            return self.server.receive_pending(self.room, self.id)
        except EOFError:
            return None  # messages were already fetched
        except LookupError:
            raise NotImplementedError('Fetch from the beginning and warn the user')

    def _wait_message(self):
        pass


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
        for author, message in client.receive_message():
            print('{0}: {1}'.format(author, message))

finally:
    print("".join(Pyro4.util.getPyroTraceback()))
