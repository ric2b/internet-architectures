import Pyro4


class ServerInfo:
    def __init__(self, server_uri):
        self.clients = 0
        self.rooms = {}
        self._server = Pyro4.Proxy(server_uri)

    def create_room(self, room):
        self.rooms[room] = 0
        # todo: use the actual method from the server


class NameServer:

    def __init__(self, room_size):
        self.rooms = {}
        self.room_size = room_size
        self.room_size_increment = 0.5*room_size
        self.servers = {}
        self._server_order = []  # for round robin assignment of rooms to servers
        self._next_server = 0

    def register_server(self, server_uri):
        if server_uri in self._server_order:
                raise ValueError('Server already registered')

        self.servers[server_uri] = ServerInfo(server_uri)
        self._server_order.append(server_uri)

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
        self.rooms[room_name] = {server}
        return server

    def join_room(self, room_name):
        if room_name in self.rooms:  # If the room is already created
            # look over the servers for the room
            for server in self.rooms[room_name].servers:
                # if any has less than self.room_size clients, send the client
                if self.servers[server].clients < self.room_size:
                    return server

            # went trough all the current servers, all full
            print('Get another server for the room')
            raise NotImplementedError

            # All servers completely full, raise self.room_size?
            # self.room_size += self.room_size_increment
            # self.rooms[room_name].add(server)

        else:  # room doesn't exist yet, create it
            return self.create_room(room_name)

    def register_client(self, server, room):
        self.servers[server].rooms[room] += 1

    def remove_client(self, server, room):
        self.servers[server].rooms[room] -= 1

        if self.servers[server].clients == 0:  # room closed if the server no longer has users
            self.servers[server].rooms.pop(room)  # the room is no longer on the server
            self.rooms[room].remove(server)  # the room no longer uses this server
            if len(self.rooms[room]) <= 0:
                self.rooms.pop(room)  # if the room has no more servers, close

if __name__ == "__main__":

    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
    Pyro4.config.SERIALIZER = 'pickle'

    daemon = Pyro4.Daemon()
    uri = daemon.register(NameServer(4), 'server')
    print("Ready. Object uri =", uri)
    daemon.requestLoop()
