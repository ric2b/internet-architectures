import socket
from unittest import TestCase
from chat_server import ChatServer, Address


class TestChatServer(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestChatServer, self).__init__(*args, **kwargs)

        # create a chat server
        self.address = Address(socket.gethostname(), socket.htons(5000))
        self.server = ChatServer(self.address, 5)

    def test_request_id(self):
        """
        Tests the request_id method. It calls the method and prints the returned
        client id and verifies if the address returned is the same as the server's.
        It also verifies if the id was registered in the clients dictionary.
        """

        client_id, address = self.server.request_id()

        print(client_id)
        # the returned address must be the same of the server
        self.assertEqual(self.address, address)
        # the clients dictionary must have only one client id reserved with
        # no client information
        self.assertEqual(len(self.server.clients), 1)
        self.assertIsNone(self.server.clients[client_id])

