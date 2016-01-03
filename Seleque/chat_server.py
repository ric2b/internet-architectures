import Pyro4

from collections import namedtuple
from chat_room import ChatRoom
from client_id import ClientId
from message import Message
from name_server import NameServer, InvalidIdError
from room_id import RoomId

name_server_uri = 'PYRO:name_server@localhost:55067'

Address = namedtuple('Address', ['ip_address', 'port'])


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

    def register(self, room_id: RoomId, client_id: ClientId, client_uri: Pyro4.URI, nickname: str = None):
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

    def send_message(self, room_id: RoomId, client_id: ClientId, message: Message):
        """
        Sends a message to all the clients in the server. Puts the message in the
        message buffer and notifies all registered clients of the new message. If
        there any client with a broken connection they are removed.

        :param room_id: id of the room to send the message to.
        :param client_id: id of the client sending the message.
        :param message: message to be sent.


        """
        # force the sender id to be the client id
        message.sender_id = client_id
        self.rooms[room_id].add_message(message)

        # notify all clients of a new message
        clients_to_remove = []
        for client_info in self.rooms[room_id]:
            try:
                client_info.client.notify_message(message)
            except Pyro4.errors.CommunicationError:
                # this client has a broken connection
                clients_to_remove.append(client_info.client_id)

        # remove the clients with broken connections
        for client_id in clients_to_remove:
            self.rooms[room_id].remove(client_id)

    def register_on_nameserver(self, self_uri: Pyro4.core.URI):
        """
        Registers the server in the name server.
        :param self_uri: uri of the server.
        """
        self.uri = self_uri
        self.name_server.register_server(self.uri)


if __name__ == "__main__":

    # set pickle as the serializer used by pyro
    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
    Pyro4.config.SERIALIZER = 'pickle'

    server = ChatServer(10)
    # register the server in the pyro daemon
    daemon = Pyro4.Daemon()
    uri = daemon.register(server, 'chat_server')
    print(uri)
    server.register_on_nameserver(uri)
    daemon.requestLoop()
