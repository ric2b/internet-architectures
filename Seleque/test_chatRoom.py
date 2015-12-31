from unittest import TestCase
from chat_room import ChatRoom
from circular_list import PacketId
from client_id import ClientId
from client_information import ClientInformation
from room_id import RoomId


class TestChatRoom(TestCase):

    def setUp(self):
        self.room = ChatRoom(RoomId, "room name", 10)

    def test_remove(self):
        """
        Tests removing a registered client.
        """

        client_id = ClientId()
        client_info = ClientInformation(client_id, message_id=PacketId(10))

        self.room.register(client_id, client_info)
        self.assertDictEqual(self.room.clients, {client_id: client_info})

        self.room.remove(client_id)
        self.assertDictEqual(self.room.clients, {}).__hash__()

    def test_remove_non_existent_client(self):
        """
        Tests if the remove method raises a LookupError when trying to remove a
        client that does not exist in the room.
        """

        with self.assertRaises(LookupError):
            self.room.remove(ClientId())
