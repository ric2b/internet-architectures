class CircularList:

    def __init__(self, size, init=0):
        self.size = size
        self.turns = 0
        self.list = []

        for position in range(size):
            self.list.append(init)

        self.oldest_position = 0
        self.newest_position = 0

    def circular_position(self, position):
        return position % self.size

    def append(self, data):

        self.newest_position += 1

        if self.newest_position >= self.size:
            self.newest_position = 0
            self.turns += 1

        self.list[self.newest_position] = data

        if self.turns > 0:
            self.oldest_position = (self.newest_position + 1) % self.size

        return self.turns

    def get_message(self, position, turns):
        if turns == self.turns:
            pass
        return self.list[position]

    def get_messages_newer_than(self, position):
        if position > self.newest_position:
            return self.list[position:] + self.list[:self.newest_position]
        else:
            return self.list[position:self.newest_position]

    def get_newest_position(self):
        return self.newest_position, self.list[self.newest_position]

    def get_oldest_position(self):
        return self.oldest_position, self.list[self.oldest_position]

    def size(self):
        if self.turns > 0:

            return self.size
        else:
            return self.newest_position

    def __str__(self):
        return self.list.__str__()
