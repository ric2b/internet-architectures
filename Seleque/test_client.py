from unittest import TestCase
from client import Client


class TestClient(TestCase):

    """
    Tests the client's operation. This test must be run with a chat server running in the
    background.  The server uri must be copied to the class variable 'uri'.
    """

    uri = "PYRO:server@localhost:60806"

    messages = ["Gentlemen, you can't fight in here! This is the War Room!",
                "Man who catch fly with chopstick accomplish anything.",
                "If you build it, he will come.",
                "I'm gonna make him an offer he can't refuse.",
                "Life is a box of chocolates, Forrest. You never know what you're gonna get."
                ]

    def test_register(self):
        """
        Checks if the registration was successful. After the successful registration
        the client id is no longer None.
        """

        client = Client()
        self.assertIsNone(client.id)
        client.register(self.uri)
        self.assertIsNotNone(client.id)

    def test_send_and_receive(self):
        """
        Test with one client sending a message and receiving its own message.
        The messages sent and receives must be equal.
        """

        client = Client()
        client.register(self.uri)
        self.assertIsNotNone(client.id)

        sent_message = "a very good messsage"
        client.send_message(sent_message)
        self.assertEqual(client.receive_message(), [sent_message])

    @staticmethod
    def create_clients(count: int) -> list:
        clients = []
        for i in range(count):
            clients.append(Client())

        return clients

    def test_multiple_clients(self):

        clients = self.create_clients(5)

        for client in clients:
            client.register(self.uri)
            self.assertIsNotNone(client.id)

        for client, message in zip(clients, self.messages):
            client.send_message(message)

        # every client should receive a list with all the sent messages
        for client in clients:
            self.assertEqual(client.receive_message(), self.messages[:len(clients)])
