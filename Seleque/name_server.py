import uuid


class RoomInfo:
    def __init__(self, name):
        self.name = name
        self.clients = {}
        self.servers = []

    def add_server(self, server_index):
        self.servers.append(server_index)

    def add_client(self, client, server_address):
        self.clients[client] = server_address

    def __eq__(self, other):
        return True if self.clients == other.clients and self.servers == other.servers else False


class ServerInfo:
    def __init__(self, address):
        self.address = address
        self.clients = {}
        self.rooms = []

    def create_room(self, room):
        return

    def add_client(self, client, room):
        return

    def __eq__(self, other):
        return True if self.address == other.address and self.clients == other.clients \
                       and self.rooms == other.rooms else False


class NameServer:

    def __init__(self, room_size):
        self.rooms = {}
        self.room_size = room_size
        self.servers = []
        self._next_server = 0
        self.clients = {}

    def register_server(self, address):
        for server in self.servers:
            if server.address == address:
                raise ValueError('Server already registered')

        self.servers.append(ServerInfo(address))

    def list_servers(self):
        servers = []
        for server in self.servers:
            servers.append(server.address)

    def list_rooms(self):
        return set(self.rooms.keys())

    def create_room(self, room_name):
        try:
            server = self.servers[self._next_server]
            self._next_server = (self._next_server + 1) % len(self.servers)

        except IndexError:  # maybe some servers went down and the list is now smaller
            try:
                server = self.servers[0]
            except IndexError:  # There are no servers
                raise ConnectionRefusedError('The system has no servers registered')

        server.create_room(room_name)
        return server.address

    def join_room(self, room_name):
        if room_name in self.rooms:  # If the room is already created
            # look over the servers for the room
            for server_address in self.rooms[room_name].servers:
                for server in self.servers:
                    if server.address == server_address:
                        # if any has less than self.room_size clients, send the client
                        if len(server.clients) < self.room_size:
                            return server_address

            # went trough all the servers, all full
            print('Get another server for the room')
            raise NotImplementedError

        else:  # room doesn't exist yet, create it
            server = self.create_room(room_name)
            room = RoomInfo(room_name)
            room.add_server(server)

            self.rooms[room_name] = room
            return server




