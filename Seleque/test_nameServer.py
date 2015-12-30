from unittest import TestCase
from name_server import NameServer, ServerInfo, RoomInfo


class TestNameServer(TestCase):

    def setUp(self):
        self.name_server = NameServer(4)

    def test_list_rooms(self):
        self.assertEqual(self.name_server.list_rooms(), set())

    def test_create_room(self):
        pass

    def test_join_room(self):
        self.name_server.register_server('127.0.0.1:9090')
        self.name_server.join_room('War Room')

        self.assertEqual(self.name_server.list_rooms(), {'War Room'})

        self.name_server.join_room('Peace Room')
        self.assertEqual(self.name_server.list_rooms(), {'War Room', 'Peace Room'})

        # Test if it avoids duplicates
        self.name_server.join_room('Peace Room')
        self.assertEqual(self.name_server.list_rooms(), {'War Room', 'Peace Room'})

    def test_register_server(self):
        self.name_server.register_server('127.0.0.1:9090')
        self.assertEqual(self.name_server.servers, [ServerInfo('127.0.0.1:9090')])

        with self.assertRaises(ValueError):
            self.name_server.register_server('127.0.0.1:9090')


