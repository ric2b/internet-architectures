import socket
import threading
import uuid
from collections import namedtuple

import Pyro4

from chat_room import ChatRoom
from circular_list import CircularList
from client_id import ClientId
from name_server import NameServer, InvalidIdError
from room_id import RoomId

name_server_uri = 'PYRO:name_server@localhost:63669'

Address = namedtuple('Address', ['ip_address', 'port'])


class ClientInformation:

    """
    Holds all information that might be stored by the server for each client.
    This must be a class and not a namedtuple because they are immutable and the attributes
    can not be altered.
    """

    def __init__(self, message_id, client, nickname: str = None):
        self.nickname = nickname
        self.message_id = message_id
        self.client = client

    def __str__(self):
        return "Info(id=%s: %s)" % (self.nickname, "connected" if self.connection else "unconnected")


class ChatServer:
    def __init__(self, buffer_size):
        """
        Initializes the messages buffer. Creates an empty dictionary with all the
        mapping the clients ids to their information. Registers the server in the
        pyro daemon.

        :param address: the complete address for the server to bound to.
        :param buffer_size: the size of the message buffer.
        """

        self.buffer_size = buffer_size
        self.rooms = {}  # type: dict[RoomId: ChatRoom]
        self.uri = None  # type: Pyro4.URI
        self.name_server = Pyro4.Proxy(name_server_uri)  # type: NameServer

    def register(self, room_id: RoomId, client_id: ClientId, client_uri: Pyro4.URI, nickname: str):
        """
        Registers the client in a room of the chat server. Establishes a pyro connection
        with the client and adds the client to the room associating him with the given
        nickname.

        :param room_id: id of the room to register to.
        :param client_id: id of the client to register.
        :param client_uri: uri of the client who wants to register.
        :param nickname: nickname to associate with the client.
        :raises KeyError: if the room does not exist in the server.
        :raises InvalidIdError: if the client id is not correctly registered in the name server.
        :raises ValueError: if the client id is already registered in the room.
        """
        # create a pyro connection with the client
        client = Pyro4.Proxy(client_uri)

        try:
            self.rooms[room_id].register(client_id, client, nickname)
        except KeyError:
            raise KeyError("there is no room with id=", str(room_id))

        try:
            # register the client in the name server
            self.name_server.register_client(client_id, self.uri, room_id, nickname)
        except InvalidIdError:
            # the client id provided is not registered in the name server
            # the registration failed
            self.rooms[room_id].remove(client_id)
            raise InvalidIdError

    # TODO adjust this method when implementing room sharing
    def create_room(self, room_id: RoomId):
        """
        Creates a new room in the server.

        :param room_id: id for the new room.
        """
        if room_id in self.rooms:
            raise ValueError("there is already a room with the id=", room_id)

        self.rooms[room_id] = ChatRoom(room_id, self.buffer_size)

    def send_message(self, room, client_id: uuid, message):
        """
        Sends a message to all the clients in the server. Puts the message in the
        message buffer and notifies all registered clients of the new message. If
        there any client with a broken connection they are removed.

        :param room:
        :param client_id:
        :param message: message to be sent.
        """

        self.rooms[room].append((self.nicknames[client_id], message))

        # notify all clients of a new message
        clients_to_remove = []
        room_clients = [self.clients[client] for client in self.room_clients[room]]
        for client in room_clients:
            try:
                client.connection.send("NEW MESSAGE".encode())
            except AttributeError:
                # the client is no completely registered yet
                # ignore this client and move to the next
                pass
            except socket.error:
                # this client has a broken connection
                client.connection.close()
                clients_to_remove.append(client)

        # remove the clients with broken connections
        for client in clients_to_remove:
            self.clients.pop(client)
            self.room_clients[room].pop(client)

    def receive_pending(self, room: str, client_id):
        """
        Returns a list with all the messages in the message queue that the client
        has not received.

        :param room:
        :param client_id:
        :return: list with the next messages in the message queue.
        """

        client_info = self.clients[client_id]
        current_index, message_list = self.rooms[room].get_since(client_info.message_id)
        self.clients[client_id].message_id = current_index

        return message_list

    def start_loop(self, self_uri: Pyro4.core.URI):
        """
        Starts the chat server putting it in a loop waiting for new requests.
        :param self_uri:
        """
        self.uri = self_uri
        self.name_server.register_server(self.uri)
        self.start_register()

    # TODO must be reimplemented
    def start_register(self):
        pass


if __name__ == "__main__":

    # set pickle as the serializer used by pyro
    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
    Pyro4.config.SERIALIZER = 'pickle'

    server = ChatServer(Address(socket.gethostname(), socket.htons(5000)), 10)
    # register the server in the pyro daemon
    daemon = Pyro4.Daemon()
    uri = daemon.register(server, 'chat_server')
    print(uri)
    server.start_loop(uri)
    daemon.requestLoop()
