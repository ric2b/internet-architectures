"""Chat Server.

Usage:
  chat_server.py <webserver-url> [--uri=<nameserver-uri> | --file=<file>]
  chat_server.py (-h | --help)

Options:
  -h --help     Show this screen.

"""
import Pyro4

from collections import namedtuple
from requests import post

from chat_room import ChatRoom
from client_id import ClientId
from message import Message
from name_server import NameServer, InvalidIdError
from room_id import RoomId
from docopt import docopt


def main():
    arguments = docopt(__doc__)

    if arguments['--uri']:
        name_server_uri = arguments['--uri']
    else:
        name_server_uri_file = arguments['--file'] if arguments['--file'] else "nameserver_uri.txt"
        with open(name_server_uri_file) as file:
            name_server_uri = file.readline()

    webserver_url = arguments['<webserver-url>']

    print("Using:")
    print("\tname server URI:", name_server_uri)
    print("\tweb server URL:", webserver_url)
    print()

    # set pickle as the serializer used by pyro
    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
    Pyro4.config.SERIALIZER = 'pickle'

    server = ChatServer(webserver_url, name_server_uri)
    # register the server in the pyro daemon
    daemon = Pyro4.Daemon()
    uri = daemon.register(server, 'chat_server')
    print("My URI: ", uri)

    server.register_on_nameserver(uri)
    print("registered on the name server")

    try:
        daemon.requestLoop()
    except KeyboardInterrupt:
        pass
    server.leave()

Address = namedtuple('Address', ['ip_address', 'port'])


class ChatServer:
    def __init__(self, webserver_url, name_server_uri):
        """
        Initializes the messages buffer. Creates an empty dictionary with all the
        mapping the clients ids to their information. Registers the server in the
        pyro daemon.
        """
        self.webserver_url = webserver_url
        self.name_server_uri = name_server_uri

        self.rooms = {}  # type: dict[RoomId: ChatRoom]

        # store all the servers to which it is connected
        # associating a server uri with a server
        self.servers = {}  # type: dict[Pyro4.URI: ChatServer]

        # associates the rooms with the server uris
        self.room_server_uris = {}  # type: dict[RoomId: set[Pyro4.URI]]

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
            self.rooms[room_id].register(client_id, client)
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

    def create_room(self, room_id: RoomId):
        """
        Creates a new room in the server.

        :param room_id: id for the new room.
        :raises ValueError: if the room already exists.
        """
        if room_id in self.rooms:
            raise ValueError("there is already a room with the id=", room_id)

        self.rooms[room_id] = ChatRoom(room_id)
        self.room_server_uris[room_id] = set()

        print("ROOM: created room '{}'".format(room_id))

    def remove_room(self, room_id: RoomId):
        """
        Removes a room from the server.
        :param room_id: id of the room to be removed.
        """

        del self.rooms[room_id]
        del self.room_server_uris[room_id]

        print("ROOM: closing room '{}' because there are no clients connected".format(room_id))

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

        servers_to_remove = []  # list with the servers that need to be removed

        # export the message to all of the servers sharing the room
        for server_uri in self.room_server_uris[room_id]:
            try:
                self.servers[server_uri].share_message(room_id, message)
            except Pyro4.errors.CommunicationError:
                # server has failed
                servers_to_remove.append(server_uri)

        for server_uri in servers_to_remove:
            # notify the name server
            self.name_server.remove_server(server_uri)
            print("SERVER: lost connection with server '{}'. Name server notified.".format(server_uri))

            # remove the server from all rooms
            for uris in self.room_server_uris.values():
                uris.discard(server_uri)

            # remove the connection with the server
            del self.servers[server_uri]

        self._notify_clients(room_id, message)

        # store message in the web server
        data = {'sender_id': message.sender_id,
                'nickname': self.name_server.get_nickname(message.sender_id),
                'text': message.text}

        post(self.webserver_url + "/{}/addmessage".format(room_id), data=data)

    def register_on_nameserver(self, self_uri: Pyro4.core.URI):
        """
        Registers the server in the name server.
        :param self_uri: uri of the server.
        """
        self.uri = self_uri
        self.name_server.register_server(self.uri)

    def share_room(self, room_id: RoomId, *server_uris):
        """
        Asks the server to share a room with a list of other servers.

        :param room_id: id of the room to share.
        :param server_uris: the URIs of the servers to share the room with.
        """
        try:
            self.create_room(room_id)
        except ValueError:
            # room already exists, add the server uris to the room
            self.room_server_uris[room_id].update(server_uris)
        else:
            self.room_server_uris[room_id] = set(server_uris)

        # establish a pyro connection if the given server uris are new
        new_servers_uris = [server_uri for server_uri in server_uris if server_uri not in self.servers]
        for server_uri in new_servers_uris:
            self.servers[server_uri] = Pyro4.Proxy(server_uri)

        print("ROOM: now sharing room '{0}' with '{1}'".format(room_id, new_servers_uris))

    def unshare_room(self, room_id: RoomId, server_uri: Pyro4.URI):
        """
        Tells the server to stop sharing a room with another server.

        :param room_id: id of the room to remove server.
        :param server_uri: uri of the server to stop sharing with.
        """
        self.room_server_uris[room_id].discard(server_uri)
        # TODO remove server connection when no room is using it

        print("ROOM: no longer sharing room '{0}' with '{1}'".format(room_id, server_uri))

    def share_message(self, room_id: RoomId, message: Message):
        """
        Shares the message with the server. The server will export the message
        to all of its clients.

        :param room_id: id of the room to share the message with.
        :param message: message to share.
        """
        self._notify_clients(room_id, message)

    def _notify_clients(self, room_id: RoomId, message: Message):
        # store the clients with broken connections on this list
        clients_to_remove = []

        # notify each client
        for client_id, client in self.rooms[room_id]:
            try:
                client.notify_message(message)
            except Pyro4.errors.CommunicationError:
                # this client has a broken connection
                clients_to_remove.append(client_id)

        # remove the clients with broken connections
        for client_id in clients_to_remove:
            self.rooms[room_id].remove(client_id)
            # todo: detect if the room should close

    def leave_room(self, room_id: RoomId, client_id: ClientId):
        self.rooms[room_id].remove(client_id)
        if self.rooms[room_id].client_count == 0:
            del self.rooms[room_id]
            print("ROOM: closed room '{0}' since it had no more clients".format(room_id))
        self.name_server.remove_client(client_id, self.uri, room_id)

    def leave(self):
        self.name_server.remove_server(self.uri)


if __name__ == "__main__":
    main()
