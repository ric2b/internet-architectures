from unittest import TestCase
from name_server import NameServer


class TestNameServer(TestCase):

    def setUp(self):
        self.name_server = NameServer()

    def test_list_rooms(self):
        self.name_server.rooms = ['War Room', 'Peace Room']

        self.assertEqual(self.name_server.list_rooms(), ['War Room', 'Peace Room'])

    def test_join_room(self):
        self.name_server.rooms = ['War Room']

        self.name_server.join_room('Peace Room')
        self.assertEqual(self.name_server.rooms, ['War Room', 'Peace Room'])

        # Test if it avoids duplicates
        self.name_server.join_room('Peace Room')
        self.assertEqual(self.name_server.rooms, ['War Room', 'Peace Room'])




