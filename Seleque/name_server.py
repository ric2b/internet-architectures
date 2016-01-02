import Pyro4
import uuid


class ServerInfo:
    def __init__(self, server_uri):
        self.clients = 0
        self.rooms = {}
        self._server = Pyro4.Proxy(server_uri)

    def create_room(self, room: str):
        self._server.create_room(room)
        self.rooms[room] = 0

    def take_down(self):
        raise NotImplementedError
        # todo: a way for the name server to take down servers, if issues are detected


class NameServer:

    def __init__(self, room_size: int):
        self.rooms = {}
        self.room_size = room_size
        self.room_size_increment = 0.5*room_size
        self.clients = set()
        self.servers = {}
        self._server_order = []  # for round robin assignment of rooms to servers
        self._next_server = 0

    def register_server(self, server: Pyro4.URI):
        if server in self._server_order:
                raise ValueError('Server already registered')

        self.servers[server] = ServerInfo(server)
        self._server_order.append(server)

        #  self.rooms['testing'] = server
        #  self.servers[server].rooms['testing'] = 0

    def remove_server(self, server: Pyro4.URI):
        self._server_order.remove(server)

        for room in self.servers[server].rooms:  # for each room served by the server...
            self.rooms[room].remove(server)  # remove the server from the room's list

        self.servers.pop(server)

    def list_servers(self):
        return list(self.servers.keys())

    def list_rooms(self):
        return list(self.rooms.keys())

    def list_users(self):
        return list(self.clients)

    def create_room(self, room: str):
        """
        finds a server and starts a NEW room on it
        :param room: str
        :return server: uri
        """
        try:
            server = self._server_order[self._next_server]  # Round robin distribution of rooms
            self._next_server = (self._next_server + 1) % len(self._server_order)

        except IndexError:  # Maybe some servers went down and the list is now smaller
            try:
                server = self._server_order[0]
            except IndexError:  # There are no servers
                raise ConnectionRefusedError('The system has no servers registered')

        self.servers[server].create_room(room)
        self.rooms[room] = {server}

        print('created room {0} on server {1}'.format(room, server))

        return server

    def join_room(self, room: str):
        """
        the client requests to join a room and gets the server uid.
        if the room doesn't exist, it's created in the process of this call.
        :param room: str
        :return server: uri
        """
        if room in self.rooms:  # If the room is already created
            # look over the servers for the room
            for server in self.rooms[room]:
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
            return self.create_room(room)

    def register_client(self, server: Pyro4.URI, room: str):
        """
        Used so that the name server can keep track of how many clients each server has, by room.
        :param server: uri
        :param room: str
        :return client: uuid
        """
        client_id = uuid.uuid4()
        self.clients.add(client_id)
        self.servers[server].rooms[room] += 1

        return client_id

    def remove_client(self, client: uuid, server: Pyro4.URI, room: str):
        """
        Used so that the name server can keep track of how many clients each server has, by room.
        :param client: uuid
        :param server: uri
        :param room: str
        """
        self.clients.discard(client)
        self.servers[server].rooms[room] -= 1

        if self.servers[server].clients == 0:  # room closed if the server no longer has users
            self.servers[server].rooms.pop(room)  # the room is no longer on the server
            self.rooms[room].remove(server)  # the room no longer uses this server
            if len(self.rooms[room]) <= 0:
                self.rooms.pop(room)  # if the room has no more servers, close
                print('closed room {0} on server {1}'.format(room, server))

if __name__ == "__main__":

    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
    Pyro4.config.SERIALIZER = 'pickle'

    daemon = Pyro4.Daemon()
    uri = daemon.register(NameServer(4), 'name_server')
    print("Ready. Object uri =", uri)
    daemon.requestLoop()
