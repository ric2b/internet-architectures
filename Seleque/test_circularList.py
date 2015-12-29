from unittest import TestCase
from circular_list import CircularList
from time import sleep


class TestCircularList(TestCase):

    message1 = "Gentlemen, you can't fight in here! This is the War Room!"
    message2 = "Man who catch fly with chopstick accomplish anything."
    message3 = "If you build it, he will come."
    message4 = "I'm gonna make him an offer he can't refuse."
    message5 = "Life is a box of chocolates, Forrest. You never know what you're gonna get."

    buffer_size = 4
    # Assume the buffer is large enough that it won't be overwritten in a millisecond
    ignore_timing = True

    def setUp(self):
        self.buffer = CircularList(self.buffer_size)

    def test_append(self):
        self.buffer.append(self.message1)

        self.assertEqual(self.buffer.get_newest()[1], self.message1)

    def test_get_newest(self):
        self.buffer.append(self.message1)
        self.buffer.append(self.message2)

        self.assertEqual(self.buffer.get_newest()[1], self.message2)

    def test_get_oldest(self):
        self.buffer.append(self.message1)
        self.buffer.append(self.message2)

        self.assertEqual(self.buffer.get_oldest()[1], self.message1)

    def test_get_next(self):
        id_packet = self.buffer.append(self.message1)
        self.buffer.append(self.message2)

        self.assertEqual(self.buffer.get_next(id_packet)[1], self.message2)

    def test_get_since(self):
        id_packet = self.buffer.append(self.message1)
        self.buffer.append(self.message2)
        if self.ignore_timing:
            sleep(0.01)
        self.buffer.append(self.message3)
        message_list = [self.message2, self.message3]

        new_id_packet, received_messages = self.buffer.get_since(id_packet)
        self.assertEqual(received_messages, message_list)

        with self.assertRaises(EOFError):
            self.buffer.get_since(new_id_packet)

    def test_get_since_EOF(self):
        id_packet = self.buffer.append(self.message1)
        self.buffer.append(self.message2)
        self.buffer.append(self.message3)
        if self.ignore_timing:
            sleep(0.01)
        self.buffer.append(self.message4)
        self.buffer.append(self.message5)

        with self.assertRaises(LookupError):
            self.buffer.get_since(id_packet)


