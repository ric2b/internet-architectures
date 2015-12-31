import uuid
import Pyro4


class RoomInfo:
    def __init__(self, name):
        self.name = name
        self.clients = {}
        self.servers = []

    def add_server(self, server_index):
        self.servers.append(server_index)

    def add_client(self, client, server_address):
        self.clients[client] = server_address

    def remove_client(self, client):
        return self.clients.pop(client)

    def __eq__(self, other):
        return True if self.clients == other.clients and self.servers == other.servers else False


class ServerInfo:
    def __init__(self):
        self.clients = 0
        self.rooms = set()

    def create_room(self, room):
        self.rooms.add(room)
        raise NotImplementedError


class NameServer:

    def __init__(self, room_size):
        self.rooms = {}
        self.room_size = room_size
        self.servers = {}
        self.clients = set()
        self._server_order = []
        self._next_server = 0

    def register_server(self, new_address):
        if new_address in self._server_order:
                raise ValueError('Server already registered')

        self.servers[new_address] = ServerInfo()
        self._server_order.append(new_address)

    def remove_server(self, server):
        raise NotImplementedError

    def list_servers(self):
        return list(self.servers.keys())

    def list_rooms(self):
        return list(self.rooms.keys())

    def create_room(self, room_name):
        try:
            server = self._server_order[self._next_server]  # Round robin distribution of rooms
            self._next_server = (self._next_server + 1) % len(self._server_order)

        except IndexError:  # Maybe some servers went down and the list is now smaller
            try:
                server = self._server_order[0]
            except IndexError:  # There are no servers
                raise ConnectionRefusedError('The system has no servers registered')

        self.servers[server].create_room(room_name)
        return server

    def join_room(self, room_name):
        if room_name in self.rooms:  # If the room is already created
            # look over the servers for the room
            for server in self.rooms[room_name].servers:
                # if any has less than self.room_size clients, send the client
                if self.servers[server].clients < self.room_size:
                    return server

            # went trough all the servers, all full
            print('Get another server for the room')
            raise NotImplementedError

        else:  # room doesn't exist yet, create it
            server = self.create_room(room_name)
            room = RoomInfo(room_name)
            room.add_server(server)

            self.rooms[room_name] = room
            return server

    def register_client(self, room, server):
        client_id = uuid.uuid4()
        self.clients += client_id
        self.servers[server].clients += 1
        self.rooms[room].addclient(client_id, server)

        return client_id

    def remove_client(self, client, room):
        self.clients.discard(client)
        server = self.rooms[room].remove_client(client)
        self.servers[server].clients -= 1

        if self.servers[server].clients == 0:
            raise NotImplementedError


if __name__ == "__main__":

    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
    Pyro4.config.SERIALIZER = 'pickle'

    daemon = Pyro4.Daemon()
    uri = daemon.register(NameServer(4), 'server')
    print("Ready. Object uri =", uri)
    daemon.requestLoop()
