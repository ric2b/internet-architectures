import threading
from collections import deque

import Pyro4

from chat_server import ChatServer
from client_id import ClientId
from message import Message
from name_server import NameServer, InvalidIdError
from room_id import RoomId

name_server_uri = 'PYRO:name_server@localhost:55067'


class RegisterError(Exception):
    pass


class Client:

    """
    Implements all the clients actions and monitors its state.
    """

    def __init__(self):

        self.id = None  # type: ClientId
        self.room_id = None
        self.server = None
        self.name_server = Pyro4.Proxy(name_server_uri)  # type: NameServer

        # messages queue
        self.message_queue = deque()

        # pyro daemon for the client
        # this must be stored to enable a clean shutdown of the client
        self.daemon = Pyro4.Daemon()
        self.client_uri = None

        # synchronizes the accesses to the message buffer
        self.lock = threading.Lock()
        # used to signal the existence of new messages
        self.semaphore = threading.Semaphore(0)

    def _join_room(self, room_id: RoomId, nickname: str):
        """
        Joins a room with the given nickname.

        :param room_id: id of the room to register to.
        :param nickname: nickname to assign the client.
        """
        joined_successfully = False
        while not joined_successfully:
            # requests a server URI and a client id from the name server
            client_id, server_uri = self.name_server.join_room(room_id)

            # generate the client's uri from the client id in order to be unique
            client_uri = self.daemon.register(self, str(client_id))

            # get the server where from the server uri
            server = Pyro4.Proxy(server_uri)  # type: ChatServer
            try:
                # register the client in the server
                server.register(room_id, client_id, client_uri, nickname)
            except InvalidIdError:
                # retry to register
                continue
            else:
                joined_successfully = True
                self.server = server
                self.client_uri = client_uri
                self.id = client_id
                self.room_id = room_id

            # initialize the pyro service for the client
            threading.Thread(target=self.daemon.requestLoop).start()

    def _send_message(self, message: Message):
        """
        Sends a message to all of the clients in the chat server.

        :param message: message to be sent.
        """

        self.server.send_message(self.room_id, self.id, message)

    def notify_message(self, message: Message):
        with self.lock:
            self.message_queue.append(message)
        # indicate that there is a new message
        self.semaphore.release()

    def _receive_message(self):
        """
        Receives a message from the chat server. If there is no message available, it
        blocks until a new message is available.

        :return: the received message.
        """
        # block until there is a new message
        self.semaphore.acquire()
        with self.lock:
            message = self.message_queue.popleft()

        return message


# noinspection PyProtectedMember
def receive(client: Client):
    while True:
        print(client._receive_message())


# noinspection PyProtectedMember
def send(client: Client):
    while True:
        text = input("message: ")
        client._send_message(Message(client.id, text))

if __name__ == "__main__":

    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
    Pyro4.config.SERIALIZER = 'pickle'

    client = Client()
    # noinspection PyProtectedMember
    client._join_room(RoomId(), "david")

    thread1 = threading.Thread(target=receive, args=[client])
    thread2 = threading.Thread(target=send, args=[client])

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
