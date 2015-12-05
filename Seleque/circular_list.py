from datetime import datetime, timezone
from collections import namedtuple


class CircularList:

    def __init__(self, size: int):
        self._size = size
        self._list = [None] * size  # list of self._message_tuple's
        self._newest = -1
        self._message_tuple = namedtuple('message_tuple', 'date contents')

    def append(self, message):
        """
        add a message to the list, returns the corresponding index and date
        :param message : (?)
        :return index : (int)
        :return date : (datetime)
        """
        self._newest = (self._newest + 1) % self._size
        message_tuple = self._message_tuple(contents=message, date=datetime.now(timezone.utc))
        self._list[self._newest] = message_tuple

        return self._newest, message_tuple.date

    def get_newest(self):
        """
        get the most recent message on the list
        :return index : (int)
        :return date : (datetime)
        :return contents : (?)
        """
        if self._newest != -1:
            index = self._newest
            return index, self._list[index].date, self._list[index].contents
        else:
            raise LookupError('Message list is still empty')

    def get_oldest(self):
        """
        get the oldest message on the list
        :return index : (int)
        :return date : (datetime)
        :return contents : (?)
        """
        if self._list[-1] is not None:  # if the list is filled until the last element
            index = (self._newest + 1) % self._size
        else:
            index = 0

        try:
            return index, self._list[index].date, self._list[index].contents
        except AttributeError:
            raise LookupError('List is empty')

    def get_next(self, index: int, date: datetime):
        """
        get the message after the given one
        :param index (int)
        :param date (datetime)
        :return: index, date and contents of the next message
        """
        try:
            indexed_message = self._list[index]
        except AttributeError:
            raise LookupError("Provided index is empty")

        if indexed_message.date == date:  # all good, get the next message
            next_index = (index + 1) % self._size
            next_message = self._list[next_index]

            try:
                if date < next_message.date:  # the next message is indeed more recent
                    return next_index, self._list[next_index].date, self._list[next_index].contents
                else:
                    raise EOFError('No next data, cool down a bit')

            except AttributeError:  # The list hasn't yet turned over
                raise EOFError('No next data, cool down a bit')
        else:
            raise LookupError('Data has been overwritten, sorry for your loss')

    def get_since(self, index: int, date: datetime):
        """
        gets all messages since the given one.
        returns the index and date of the latest message and a list with all messages read

        :param index: int
        :param date: datetime
        :return: index, date, list of message contents
        """
        messages = []
        try:
            while True:
                index, date, contents = self.get_next(index=index, date=date)
                messages.append(contents)
        except EOFError:  # end of the list
            return index, date, messages

    def __str__(self):
        message_contents = []
        for element in self._list:
            try:
                message_contents.append(element.contents)
            except AttributeError:
                message_contents.append(None)

        return message_contents.__str__()
