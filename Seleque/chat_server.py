from collections import deque
import uuid
import Pyro4


class ChatServer:

    def __init__(self):
        self.clients = {}

    def register(self):
        client_id = uuid.uuid4()
        self.clients[client_id] = deque()
        return client_id

    def send_message(self, client_id, message):
        self.clients[client_id].append(message)

    def receive_message(self, client_id):
        message = None
        while not message:
            try:
                return self.clients[client_id].popleft()
            except KeyError:
                pass

Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
Pyro4.config.SERIALIZER = 'pickle'

daemon = Pyro4.Daemon()
uri = daemon.register(ChatServer(), 'server')
print("Ready. Object uri =", uri)
daemon.requestLoop()




