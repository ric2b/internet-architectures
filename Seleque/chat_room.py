from circular_list import CircularList
from room_id import RoomId


class ChatRoom:
    """
    A chat room allows a set of clients to communicate between each other. When a
    client sends a message all clients in the room receive that message. A room has
    a unique id that identifies it and a name that can be repeated between rooms.
    """

    def __init__(self, room_id: RoomId, name: str, buffer_capacity: int):
        """
        Initializes the room with a unique identifier. It is created a message buffer
        for the room with the given capacity.

        :param room_id: id to be assigned to the room.
        :param name: name to be assigned to the room.
        :param buffer_capacity: max capacity for the message buffer.
        """
        self.room_id = room_id
        self.name = name
        self.buffer_capacity = buffer_capacity

        # each client is associated to the last message he read
        self.clients = {}
        # buffer with all the messages for this room
        self.messages_buffer = CircularList(self.buffer_capacity)

