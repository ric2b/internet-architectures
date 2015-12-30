from unittest import TestCase
from chat_server import ChatServer


class TestChatServerSetUp(TestCase):
    def test_register(self):
        self.server = ChatServer(4)
        self.assertNotEqual(self.server.register(), self.server.register())


class TestChatServer(TestCase):

    messages = ["Gentlemen, you can't fight in here! This is the War Room!",
                "Man who catch fly with chopstick accomplish anything.",
                "If you build it, he will come.",
                "I'm gonna make him an offer he can't refuse.",
                "Life is a box of chocolates, Forrest. You never know what you're gonna get."
                ]

    def setUp(self):
        self.server = ChatServer(4)
        self.my_id = self.server.register()

    def test_send_message(self):
        self.server.send_message(self.messages[1])

        self.assertEqual(self.server.receive_pending(self.my_id), [self.messages[1]])

    def test_receive_pending(self):
        for i in range(4):
            self.server.send_message(self.messages[i])

        self.assertEqual(self.server.receive_pending(self.my_id), self.messages[:4])

    def test_receive_pending_empty(self):
        with self.assertRaises(LookupError):
            self.server.receive_pending(self.my_id)





