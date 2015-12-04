from collections import deque
import uuid
import Pyro4
from threading import Condition


class ChatServer:

    def __init__(self):
        # each client is associated to the last message he read
        self.clients = {}
        # buffer with all the messages
        self.messages = []
        # condition to indicate that there is new messages
        self.message_available = Condition

    def register(self):
        # generate unique id for the new user
        client_id = uuid.uuid4()

        # a new user only receives the new messages sent after registering
        # assign to the user the index of the last message
        self.clients[client_id] = len(self.messages)

        return client_id

    def send_message(self, message):
        with self.message_available:
            self.messages.append(message)
            self.message_available.notifyAll()

    def receive_message(self, client_id):

        with self.message_available:
            client_last_index = self.clients[client_id]

            while client_last_index < len(self.messages):
                # there is a message available for the client
                message = self.messages[self.clients[client_id]]
                self.message_available.wait()


Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
Pyro4.config.SERIALIZER = 'pickle'

daemon = Pyro4.Daemon()
uri = daemon.register(ChatServer(), 'server')
print("Ready. Object uri =", uri)
daemon.requestLoop()




