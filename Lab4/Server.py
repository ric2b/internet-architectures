from collections import deque
import Pyro4
import uuid




class Server:

    def __init__(self):
        self.groups = {}
        self.clients = {}

    def register(self):
        client_identifier = uuid.uuid4()
        self.clients[client_identifier] = deque()
        return client_identifier

    def create_group(self, client_identifier, group_name):
        if group_name in self.groups:
            self.groups[group_name] = client_identifier

    def join_to_group(self, client_identifier, group_name):
        self.create_group(client_identifier, group_name)

    def send_message(self, client_identifier, group_name, message):
        for client in self.groups[group_name]:
            if client != client_identifier:
                self.clients[client].append((group_name, client_identifier, message))

    def receive_message(self, client_identifier, block=True):

        message = None
        while not message:
            try:
                return self.clients[client_identifier].popleft()
            except KeyError:
                pass

    def leave_group(self, client_identifier, group_name):
        self.groups[group_name].remove(client_identifier)
        self.clients[client_identifier] = deque()


