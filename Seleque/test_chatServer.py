import socket
import uuid
from unittest import TestCase
from chat_server import ChatServer, Address, ClientInformation


class TestChatServer(TestCase):

    messages = ["Gentlemen, you can't fight in here! This is the War Room!",
                "Man who catch fly with chopstick accomplish anything.",
                "If you build it, he will come.",
                "I'm gonna make him an offer he can't refuse.",
                "Life is a box of chocolates, Forrest. You never know what you're gonna get."
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
