from datetime import datetime, timezone
from collections import namedtuple

class CircularList:

    def __init__(self, size):
        self._size = size
        self._list = [None] * size
        self._newest = 0
        self._message_tuple = namedtuple('message_packet', 'date message')

    def append(self, message):
        self._newest = (self._newest + 1) % self._size
        message_tuple = self._message_tuple(contents=message, date=datetime.now(timezone.utc))
        self._list[self._newest] = message_tuple

        return self._newest, message_tuple.date

    def get_next(self, index, date):
        indexed_message = self._list[index]

        if indexed_message.date == date: # all good, get the next message
            next_index = (index + 1) % self._size
            next_message = self._list[next_index]

            if date < next_message.date: # the next message is indeed more recent
                return next_index, self._list[next_index]
            else:
                raise LookupError('No next data, cool down a bit.')
        else:
            raise LookupError('Data has been overwritten, sorry for your loss.')

    def get_since(self, index, date):

        while True:
            try:
                yield self.get_next(index=index, date=date)
            except LookupError:
                pass


    def get_oldest(self):
        pass

    def __str__(self):
        return self._list.__str__()
