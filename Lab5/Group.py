from Lab5.CircularList import CircularList
from Lab5.ClientHistory import ClientHistory


class Group:
    def __init__(self):
        self.messages = CircularList()
        self.client = ClientHistory()

    def add_client(self, client_id):
        self.client.register(client_id)
        self.client.update(client_id, self.messages.get_current_position())


