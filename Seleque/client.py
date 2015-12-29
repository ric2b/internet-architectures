
class Client:

    """ Represents a client """

    def __init__(self):
        self.id = None
        self.connection = None

    def register(self, server_uri):
        pass

    def send_message(self, message: str):
        pass

    def recv_message(self) -> str:
        pass

    def __del__(self):
        if self.connection:
            self.connection.close()
