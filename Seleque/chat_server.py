import socket
import threading
import uuid
from collections import namedtuple

import Pyro4

ServerAddress = namedtuple('ServerAddress', ['ip_address', 'port'])


class ClientInformation:

    """ Holds all information that might be stored by the server for each client """

    def __init__(self, id: int, connection: socket = None):
        self.id = id
        self.connection = connection

    def __str__(self):
        return "Info(id=%s, %s)" % (self.id, "connected" if self.connection else "unconnected")


class ChatServer(threading.Thread):

    def __init__(self):
        super().__init__()

        # stores all the clients registered in the server and maps a client id
        # to its client information
        self.clients = {}

        # create the listening socket #

        # create a socket to listen for new connections
        self.listen_socket = socket.socket()

        # DEBUG this function allows a port number to be used right after the
        # application terminates
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind the socket to the any interface and the port number 5000
        self.address = ServerAddress(socket.gethostname(), socket.htons(5000))
        self.listen_socket.bind((self.address.ip_address, self.address.port))

        # put the socket in listening mode
        self.listen_socket.listen(5)

    def register(self):
        """
        Registers a new client in the server. It assigns an unique id to the client
        and returns this id to the client. A client calls this method to obtain an
        id and to get the server's ip address and port number.

        :return: the id assign to the client and the server's address.
        """

        # generate unique id for the new user
        client_id = uuid.uuid4()
        # store the client in the set of registered clients
        self.clients[client_id] = ClientInformation(client_id)

        # TODO implement a timer for the client to establish a TCP connection

        return client_id, self.address.ip_address, self.address.port

    def run(self):
        """
        This thread is waiting for new connections and it is responsible for performing
        the second step of registration of the clients.
        """

        while True:
            # wait for a new connection
            connection, address = self.listen_socket.accept()

            # receive the client's id
            client_id = connection.recv(32)
            client_id = uuid.UUID(client_id.decode())

            try:
                # verify if there is a client registered with that id
                client_info = self.clients[client_id]

                # assign the new connection the client
                client_info.connection = connection

                # notify the client that the registration was successful
                connection.send("OK".encode())

                print(client_info)

            except KeyError:
                # there is no client with the provided id
                connection.send("ERROR".encode())


if __name__ == "__main__":

    chat_server = ChatServer()
    chat_server.start()

    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
    Pyro4.config.SERIALIZER = 'pickle'

    daemon = Pyro4.Daemon()
    uri = daemon.register(chat_server, 'server')
    print("Ready. Object uri =", uri)
    daemon.requestLoop()
