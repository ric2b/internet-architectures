import uuid


class ServerInfo:
    def __init__(self, address):
        self.address = address
        self.clients = {}
        self.rooms = []

    def create_room(self, room):
        raise NotImplementedError

    def add_client(self, client, room):
        raise NotImplementedError


class NameServer:

    def __init__(self, room_size):
        self.rooms = []
        self.room_size = room_size
        self.servers = []
        self._next_server = 0
        self.clients = {}

    def list_rooms(self):
        return self.rooms

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
        if room_name in self.rooms:
            for server in self.rooms[room_name].servers:
                if server.clients < self.room_size:
                    return server.address

        else:
            return self.create_room(room_name)

    def register_client(self, name):
        client_id = uuid.uuid4()
        self.clients[client_id] += [name]

    def register_server(self, address):
        for server in self.servers:
            if server.address == address:
                raise ValueError

        self.servers.append(ServerInfo(address))


