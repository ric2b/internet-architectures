class ClientHistory:

    def __init__(self):
        self.clients = {}

    def register(self, client_id):
        self.clients[client_id] = None

    def update(self, client_id, last_read):
        self.clients[client_id] = last_read

    def remove(self, client_id):
        del self.clients[client_id]

    def get(self, client_id):
        return self.clients[client_id]

