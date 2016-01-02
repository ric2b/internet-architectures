from socket import socket

from client_information import ClientInformation
from circular_list import CircularList
from client_id import ClientId
from room_id import RoomId


class ChatRoom:
    """
    A chat room allows a set of clients to communicate between each other. When a
    client sends a message all clients in the room receive that message. A room has
    a unique id that identifies it and a name that can be repeated between rooms.
    A room can be iterated to get each client information.
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

        # stores all the clients associated their respective information
        self.clients = {}
        # buffer with all the messages for this room
        self.messages_buffer = CircularList(self.buffer_capacity)

    def register(self, client_id: ClientId, client_info: ClientInformation = None):
        """
        Registers a new client in the room.

        :param client_id: id of the client to register.
        :param client_info: information associated with the client
        :raises ValueError: if the client is already registered
        """
        if client_id in self.clients:
            raise ValueError("a client with this id is already registered")

        self.clients[client_id] = client_info

    def remove(self, client_id):
        """
        Removes a client from the room.

        :param client_id: if of the client to be removed
        :raises LookupError: if the client does no exist in the room.
        """

        try:
            client_connection = self.clients[client_id].connection # type: socket
            if client_connection:
                client_connection.close()
        except KeyError:
            raise LookupError("client with id=%s does not exist" % (client_id,))

        del self.clients[client_id]

    def __iter__(self):
        return iter(self.clients.values())
