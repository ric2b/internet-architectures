import uuid


class ClientId:

    """
    Client identifier. This is unique for each client.
    """

    def __init__(self):
        self.id = uuid.uuid4()

    def __eq__(self, other):
        return self.id == other.id

    def __le__(self, other):
        return self.id <= other.id

    def __lt__(self, other):
        return self.id < other.id

    def __ge__(self, other):
        return self.id >= other.id

    def __gt__(self, other):
        return self.id > other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return "%s" % (self.id,)

