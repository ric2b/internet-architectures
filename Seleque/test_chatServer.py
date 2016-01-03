import socket
import uuid
from unittest import TestCase

import Pyro4

from chat_server import ChatServer, Address, ClientInformation
from client_id import ClientId
from name_server import InvalidIdError
from room_id import RoomId
from mock import MagicMock


class TestChatServer(TestCase):

    class FakeNameServer:
        def register_client(self, client_id, uri, room_id, nickname):
            pass

    @staticmethod
    def fake_pyro_proxy(uri):
        print("pyro connection: ", uri)

    def setUp(self):
        self.old_pyro_proxy = Pyro4.Proxy
        Pyro4.Proxy = TestChatServer.fake_pyro_proxy

    def tearDown(self):
        Pyro4.Proxy = self.old_pyro_proxy

    def test_register(self):

        chat_server = ChatServer(10)
        chat_server.name_server = self.FakeNameServer()

        uri = Pyro4.URI("PYRO:name_server@localhost:63669")
        nickname = "the chat server"

        # it raises a KeyError when the room does not exist
        with self.assertRaises(KeyError):
            chat_server.register(RoomId(), ClientId(), uri, nickname)

        room_id = RoomId()
        client_id = ClientId()
        chat_server.create_room(room_id)

        # there is a new room in the server with no clients
        self.assertIsNotNone(chat_server.rooms[room_id])
        self.assertEqual(len(chat_server.rooms[room_id].clients), 0)

        chat_server.register(room_id, client_id, uri, nickname)
        # there is one client in the room now
        self.assertEqual(len(chat_server.rooms[room_id].clients), 1)

        # client already exists
        with self.assertRaises(ValueError):
            chat_server.register(room_id, client_id, uri, nickname)

        chat_server.name_server.register_client = MagicMock(side_effect=InvalidIdError)

        rooms_before = chat_server.rooms
        with self.assertRaises(InvalidIdError):
            chat_server.register(room_id, ClientId(), uri, nickname)
        # the rooms was not changed
        self.assertDictEqual(rooms_before, chat_server.rooms)


class TestOldChatServer(TestCase):
    messages = ["Gentlemen, you can't fight in here! This is the War Room!",
                "Man who catch fly with chopstick accomplish anything.",
                "If you build it, he will come.",
                "I'm gonna make him an offer he can't refuse.",
                "Life is a box of chocolates, Forrest. You never know what you're gonna get.",
                "Nobody puts Baby in a corner.",
                "The cold never bothered me anyway.",
                "Well, what if there is no tomorrow? There wasn't one today.",
                "You talkin' to me?"
                ]

    def setUp(self):
        self.address = Address(socket.gethostname(), socket.htons(5000))
        self.server = ChatServer(self.address, 5)

        # generate fake id and register fake client
        self.my_id = uuid.uuid4()
        self.server.clients[self.my_id] = None
        self.server._register_client(client_id=self.my_id, connection=None)

        self.assertIsNotNone(self.server.clients[self.my_id])

    def test_request_id(self):
        """
        Tests the request_id method. It calls the method and prints the returned
        client id and verifies if the address returned is the same as the server's.
        It also verifies if the id was registered in the clients dictionary.
        """

        my_id, address = self.server.request_id()

        print(self.my_id)
        # the returned address must be the same of the server
        self.assertEqual(self.address, address)
        # the clients dictionary must have only one client id reserved with
        # no client information
        self.assertIsNone(self.server.clients[my_id])

    def test_send_and_receive_message(self):
        """
        Tests the send and receive methods. Tries to send a message and checks id the received
        message is equal to the message sent.
        """

        self.server.send_message(self.messages[1])
        self.assertEqual(self.server.receive_pending(self.my_id), [self.messages[1]])

    def test_send_and_receive_multiple_messages(self):
        """
        Tests sending and receiving multiple messages. It sends multiple messages and and checks
        if it receives the same messages when calling receive_pending.
        """

        for i in range(4):
            self.server.send_message(self.messages[i])

        self.assertEqual(self.server.receive_pending(self.my_id), self.messages[:4])

    def test_receive_empty(self):
        """
        Tests if a LookupError is raised when calling the receive_pending method with an
        empty message buffer
        """

        with self.assertRaises(LookupError):
            self.server.receive_pending(self.my_id)
