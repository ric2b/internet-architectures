import uuid
import Pyro4
from threading import Condition
from circular_list import CircularList


class ChatServer:

    buffer_size = 4

    def __init__(self):
        # each client is associated to the last message he read
        self.clients = {}
        # buffer with all the messages
        self.messages_buffer = CircularList(self.buffer_size)
        # condition to indicate that there is new messages
        self.message_available = Condition()

    def register(self):
        # generate unique id for the new user
        client_id = uuid.uuid4()

        # a new user only receives messages that are sent after he registers
        # assign to the user the index of the last message

        try:
            self.clients[client_id] = self.messages_buffer.get_newest()[0]
        except AttributeError:
            self.clients[client_id] = None

        return client_id

    def send_message(self, message):
        with self.message_available:
            self.messages_buffer.append(message)
            self.message_available.notify_all()

    def receive_message(self, client_id):

        with self.message_available:

            current_index = self.clients[client_id]

            message = None
            while not message:
                try:
                    current_index, message = self.messages_buffer.get_next(current_index)

                except EOFError:
                    self.message_available.wait()

                except LookupError:
                    # Data was lost
                    print('WARNING: TEMPORARY SOLUTION. This should fetch every message '
                          'because data was overwritten (receive_message)')

        self.clients[client_id] = current_index
        return message

    def receive_pending(self, client_id):

        current_index, message_list = self.messages_buffer.get_since(self.clients[client_id])
        self.clients[client_id] = current_index

        return message_list


if __name__ == "__main__":

    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
    Pyro4.config.SERIALIZER = 'pickle'

    daemon = Pyro4.Daemon()
    uri = daemon.register(ChatServer(), 'server')
    print("Ready. Object uri =", uri)
    daemon.requestLoop()
