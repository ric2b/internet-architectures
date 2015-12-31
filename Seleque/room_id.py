
class RoomId:

    """
    Room identifier. This is unique for each chat room.
    """

    # this counter generates an unique number for each room id created
    id_counter = 0

    def __init__(self):
        self.id = RoomId.id_counter
        RoomId.id_counter += 1

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
        return self.id

    def __str__(self):
        return "%d" % (self.id,)
