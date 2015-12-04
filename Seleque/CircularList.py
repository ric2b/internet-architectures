class CircularList:

    def __init__(self, size, init=0):
        self._size = size
        self._list = []

        for position in range(size):
            self._list.append(init)

        self._oldest = 0
        self._newest = 0

    def buffer_position(self, position):
        return position % self._size

    def append(self, data):

        self._newest = (self._newest + 1) % self._size
        self._list[self._newest] = data

    def get(self, position):
        return self._list[position % self._size]

    def get_after(self, position):
        if self.buffer_position(position) > self._newest:
            return self._list[position:] + self._list[:self._newest]
        else:
            return self._list[position:self._newest]

    def get_newest(self):
        return self._newest, self._list[self._newest]

    def get_oldest(self):
        return self._oldest, self._list[self._oldest]

    def size(self):
        if self.turns > 0:

            return self._size
        else:
            return self._newest

    def __str__(self):
        return self._list.__str__()
