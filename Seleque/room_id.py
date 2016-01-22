
class RoomId:
    """
    Room identifier. This is must be unique for each chat room.
    """

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if type(other) == str:
            return self.name == other
        else:
            return self.name == other.name

    def __le__(self, other):
        return self.name <= other.name

    def __lt__(self, other):
        return self.name < other.name

    def __ge__(self, other):
        return self.name >= other.name

    def __gt__(self, other):
        return self.name > other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name
