"""Name Server.

Usage:
  name_server.py [--url=httpserver] [--r=<room_capacity>]
  name_server.py <ipaddress> <port> [--r=<room_capacity>]
  name_server.py (-h | --help)

Options:
  -h --help         Show this screen.
  --r=<room_capacity>   Specify the initial capacity of the rooms [default: 2]
"""
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import Pyro4
import uuid
from client_id import ClientId
from room_id import RoomId
from docopt import docopt
from requests import post


# global name server
global name_server


class InvalidIdError(AttributeError):
    pass


class ServerInfo:
    def __init__(self, server_uri):
        self.clients = 0
        self.rooms = {}  # type: dict[RoomId: int]
        self._server = Pyro4.Proxy(server_uri)

    def create_room(self, room_id: RoomId):
        self._server.create_room(room_id)
        self.rooms[room_id] = 0

    def close_room(self, room_id: RoomId):
        pass
        # self._server.remove_room(room_id)

    def share_room(self, room_id: RoomId, *servers: Pyro4.URI):
        self._server.share_room(room_id, *servers)

    def unshare_room(self, room_id: RoomId, *servers: Pyro4.URI):
        self._server.unshare_room(room_id, *servers)

    def take_down(self):
        raise NotImplementedError
        # todo: a way for the name server to take down servers, if issues are detected


class RegisterServer:
    def __init__(self, room_size: int, lookup_server_url):
        self.rooms = {}  # type: dict[RoomId: list[Pyro4.URI]]
        self.room_clients = {}  # type: dict[RoomId: int]
        self.room_size = room_size
        self.room_size_increment = 0.5 * room_size
        # maps a client to its nickname
        self.clients = {}  # type: dict[uuid: str]
        self.servers = {}  # type: dict[Pyro4.URI: ServerInfo]
        # for round robin assignment of rooms to servers
        self._server_order = []  # type: [Pyro4.URI]
        self._next_server = 0

        self.lock = threading.Lock()

        self.uri = None
        self.lookup_server_url = lookup_server_url

    def register_server(self, server: Pyro4.URI):
        if server in self._server_order:
            raise ValueError('Server already registered')

        self.servers[server] = ServerInfo(server)
        self._server_order.append(server)

        print("SERVER: server '{}' has registered".format(server))

    def remove_server(self, removed_server: Pyro4.URI):
        with self.lock:
            if removed_server in self.servers:
                self._server_order.remove(removed_server)

                for room in self.servers[removed_server].rooms:  # for each room served by the server...
                    self.rooms[room].remove(removed_server)  # remove the server from the room's list
                    if self.rooms[room]:
                        for server in self.rooms[room]:
                            self.servers[server].unshare_room(room, removed_server)
                    else:
                        self.rooms.pop(room)
                        self.remove_room_from_ls(room)
                        print("ROOM: closed room '{0}', no longer on any server".format(room, removed_server))

                self.servers.pop(removed_server)
                print("SERVER: removed server '{0}' due to connection problems.".format(removed_server))

    def list_servers(self):
        return list(self.servers.keys())

    def list_rooms(self):
        return list(self.rooms.keys())

    def list_users(self):
        return list(self.clients)

    def create_room(self, room: RoomId):
        """
        finds a server and starts a NEW room on it
        :param room: str
        :return server: uri
        """
        # try to register the room in the lookup server db.
        # fails if it's already created in another register server
        if not self.register_room_in_ls(room):
            raise ConnectionAbortedError

        try:
            # Round robin distribution of rooms
            server = self._server_order[0]
            for i in range(len(self.servers)):
                server = self._server_order[self._next_server]
                self._next_server = (self._next_server + 1) % len(self._server_order)
                if room in self.rooms:
                    if server not in self.rooms[room]:
                        break

        except IndexError:  # Maybe some servers went down and the list is now smaller
            try:
                server = self._server_order[0]
            except IndexError:  # There are no servers
                raise ConnectionRefusedError('The system has no servers registered')

        try:
            self.servers[server].create_room(room)
        except ValueError:  # there are no available servers, raise the limit
            print("SERVER: increasing room size, no more free servers."
                  " done because of room '{0}'".format(room))
            self.room_size += self.room_size_increment
            raise LookupError

        try:
            self.rooms[room].append(server)
        except KeyError:  # room doesn't exist on any servers
            self.rooms[room] = [server]
            self.room_clients[room] = 0

        print("ROOM: created room '{0}' on server '{1}'".format(room, server))

        return server

    def share_room(self, room_id: RoomId, new_server: Pyro4.URI):
        servers = [server for server in self.rooms[room_id] if server != new_server]
        self.servers[new_server].share_room(room_id, *servers)

        for server in servers:
            self.servers[server].share_room(room_id, new_server)

    def join_room(self, room_id: RoomId):
        """
        the client requests to join a room and gets the server uid.
        if the room doesn't exist, it's created in the process of this call.

        :param room_id: id of the room to join.
        :return tuple with the client id and the server uri for the request room.
        """
        # generate unique id for the client
        client_id = uuid.uuid4()
        # save the client id
        self.clients[client_id] = None

        if room_id in self.rooms:  # If the room is already created
            # look over the servers for the room
            for server in self.rooms[room_id]:
                # if any has less than self.room_size clients, send the client
                if self.servers[server].rooms[room_id] < self.room_size:
                    return client_id, server

            print("ROOM: servers for room '{}' are full, getting another server".format(room_id))
            server_uri = self.create_room(room_id)
            self.share_room(room_id, server_uri)

        else:  # room doesn't exist yet, create it
            server_uri = self.create_room(room_id)

        return client_id, server_uri

    def get_nickname(self, client_id: ClientId):
        return self.clients[client_id]

    def register_client(self, client_id: ClientId, server: Pyro4.URI, room_id: RoomId, nickname: str):
        """
        Registers the client in the name server associated with the server where the
        client is registered on. It also associates the client with a nickname enabling
        any server to request the nickname of a client with its client id. Used so that
        the name server can keep track of how many clients each server has, by room.

        :param client_id: id of the client.
        :param server: uri of the server where the client is registered.
        :param room_id: id of the room where the client is registered.
        :param nickname: nickname associated with the client.
        :raises InvalidIdError: if the client id is not valid.
        """
        if client_id not in self.clients:
            # the client id is not valid
            raise InvalidIdError

        # associate the client with its nickname
        self.clients[client_id] = nickname
        # increase the count of clients in the given server and room pair
        self.servers[server].clients += 1
        self.servers[server].rooms[room_id] += 1
        self.room_clients[room_id] += 1

        return client_id

    def remove_client(self, client: uuid, server: Pyro4.URI, room: RoomId):
        """
        Used so that the name server can keep track of how many clients each server has, by room.
        :param client: uuid
        :param server: uri
        :param room: str
        """
        del self.clients[client]
        self.servers[server].clients -= 1
        self.servers[server].rooms[room] -= 1
        self.room_clients[room] -= 1

        if self.servers[server].rooms[room] <= 0:  # the server no longer has users for this room
            self.servers[server].rooms.pop(room)  # the room is no longer on the server
            self.rooms[room].remove(server)  # the room no longer uses this server

            if len(self.rooms[room]) <= 0:
                del self.rooms[room]  # if the room has no more servers, close
                self.remove_room_from_ls(room)
                print("ROOM: closed room '{0}', no longer on any server".format(room, server))
            else:
                self.servers[server].close_room(room)
                for shared_server in self.rooms[room]:
                    self.servers[shared_server].unshare_room(room, server)
                print("ROOM: room '{0}' closed on server '{1}'".format(room, server))

    def register_self_in_ls(self):
        post('{0}/register_rs'.format(self.lookup_server_url), data={'uri': self.uri})

    def remove_room_from_ls(self, room):
        post('{0}/remove_room'.format(self.lookup_server_url), data={'room_id': room})

    def register_room_in_ls(self, room):
        response = post('{0}/register_room'.format(self.lookup_server_url),
                        data={'room_id': room, 'uri': self.uri})
        if response.text == 'OK':
            return True
        else:
            return False


# noinspection PyPep8Naming
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # send code 200 response
        self.send_response(200)
        # send header first
        self.send_header('Content-type', 'text')
        self.end_headers()
        # send client count
        try:
            room_id = self.path[1:]
            self.wfile.write(str(name_server.room_clients[room_id]).encode())
            self.wfile.write(str(" clients in room '{}'".format(room_id)).encode())
        except KeyError:
            self.send_error(404, 'room not found')


if __name__ == "__main__":

    arguments = docopt(__doc__)

    if arguments['--url']:
        http_address = arguments['--url'].split(':')  # returns a list [ ipaddress, port ]
        http_address = (http_address[0], int(http_address[1]))  # convert list to a tuple and make the port an int
    elif arguments['<ipaddress>']:
        http_address = (arguments['<ipaddress>'], int(arguments['<port>']))  # the port number must be an int
    else:
        http_address = ('127.0.0.1', 8088)

    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
    Pyro4.config.SERIALIZER = 'pickle'

    name_server = RegisterServer(int(arguments['--r']), 'http://selequelookup.appspot.com')  # argument --r defaults to 2 when none is specified

    daemon = Pyro4.Daemon()
    uri = daemon.register(name_server, 'name_server')
    name_server.uri = uri
    name_server.register_self_in_ls()

    with open("nameserver_uri.txt", mode='w') as file:
        file.write(str(uri))

    threading.Thread(target=daemon.requestLoop).start()
    httpd = HTTPServer(http_address, RequestHandler)

    print("Using:")
    print("\tmy URI:", uri)
    print("\thttp server URL: {}:{}".format(http_address[0], http_address[1]))
    print("\tinitial room capacity:", arguments['--r'])

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    daemon.shutdown()
