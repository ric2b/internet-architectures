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

    def test_iteration(self):
        """
        Tests if the room iteration works correctly. When iterating through a room
        we have to iterate through the information of all clients.
        """

        client_count = 5
        client_ids = {}

        # create a set of client ids with a boolean flag to indicate if the client id
        # was visited during iteration
        for i in range(client_count):
            # initially all client ids are marked not visited
            client_ids[ClientId()] = False

        # register all client ids
        for client_id in client_ids.keys():
            self.room.register(client_id, ClientInformation(client_id, message_id=PacketId(10)))

        # iterate through the room
        for client in self.room:  # type: ClientInformation
            # verify if the client id was not already visited
            self.assertFalse(client_ids[client.client_id])
            client_ids[client.client_id] = True

        # verify if all client ids were checked
        for checked in client_ids.values():
            self.assertTrue(checked)
