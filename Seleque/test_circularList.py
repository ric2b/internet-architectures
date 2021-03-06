from unittest import TestCase

from circular_list import CircularList, PacketId


class TestPacketID(TestCase):

    def test_same(self):
        old_packet_id = PacketId(0)
        packet_id0 = PacketId(0)
        packet_id1 = PacketId(1)
        self.assertTrue(packet_id0 == old_packet_id)
        self.assertTrue(not packet_id1 == old_packet_id)

    def test_overflow(self):
        old_packet_id = PacketId(0)

        new_packet_id = PacketId(0)
        self.assertTrue(new_packet_id <= old_packet_id)

        new_packet_id = PacketId(1)
        self.assertTrue(not new_packet_id <= old_packet_id)


class TestCircularList(TestCase):

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

    buffer_size = 4

    def setUp(self):
        self.buffer = CircularList(self.buffer_size)

    def test_append(self):
        self.buffer.append(self.messages[1])

        self.assertEqual(self.buffer.get_newest()[1], self.messages[1])

    def test_get_newest(self):
        self.buffer.append(self.messages[1])
        self.buffer.append(self.messages[2])

        self.assertEqual(self.buffer.get_newest()[1], self.messages[2])

    def test_get_oldest(self):
        self.buffer.append(self.messages[0])
        self.buffer.append(self.messages[1])

        self.assertEqual(self.buffer.get_oldest()[1], self.messages[0])

    def test_get_oldest_empty(self):
        with self.assertRaises(LookupError):
            self.buffer.get_oldest()

    def test_get_oldest_overwritten(self):
        for i in range(5):
            self.buffer.append(self.messages[i])

        self.assertEqual(self.buffer.get_oldest()[1], self.messages[1])

    def test_get_next(self):
        id_packet = self.buffer.append(self.messages[1])
        self.buffer.append(self.messages[2])

        self.assertEqual(self.buffer.get_next(id_packet)[1], self.messages[2])

    def test_get_next_empty(self):
        with self.assertRaises(LookupError):
            self.buffer.get_next(None)

    def test_get_next_isLast(self):
        id_packet = self.buffer.append(self.messages[1])

        with self.assertRaises(EOFError):
            self.buffer.get_next(id_packet)

    def test_get_next_bufferFull(self):
        id_packet = None
        for i in range(self.buffer_size):
            id_packet = self.buffer.append(self.messages[i])

        with self.assertRaises(EOFError):
            self.buffer.get_next(id_packet)

    def test_get_next_overwritten(self):
        id_packet = self.buffer.append(self.messages[1])
        for i in range(self.buffer_size):
            self.buffer.append(self.messages[i])

        with self.assertRaises(LookupError):
            self.buffer.get_next(id_packet)

    def test_get_since(self):
        id_packet = self.buffer.append(self.messages[1])
        self.buffer.append(self.messages[2])
        self.buffer.append(self.messages[3])

        new_id_packet, received_messages = self.buffer.get_since(id_packet)
        self.assertEqual(received_messages, self.messages[2:4])

        with self.assertRaises(EOFError):
            self.buffer.get_since(new_id_packet)

    def test_get_since_overwritten(self):
        id_packet = self.buffer.append(self.messages[1])

        for i in range(1, 5):
            self.buffer.append(self.messages[i])

        with self.assertRaises(LookupError):
            self.buffer.get_since(id_packet)
