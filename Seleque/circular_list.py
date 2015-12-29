from datetime import datetime, timezone
from collections import namedtuple


class CircularList:

    def __init__(self, size: int):
        self._size = size
        self._list = [None] * size  # list of self._message_tuple's
        self._newest = -1
        self._data_packet = namedtuple('data_packet', 'id contents')
        self._id_packet = namedtuple('id_packet', 'index id')

        self.append('Buffer created')  # Trust me, this simplifies lots of stuff :)

    @staticmethod
    def data_id():
        return datetime.now(timezone.utc)

    def append(self, data):
        """
        add a message to the list, returns the corresponding index and date
        :param data : (?)
        :return id_packet : (namedtuple->index, id)
        """
        new_index = (self._newest + 1) % self._size
        data_id = self.data_id()

        data_packet = self._data_packet(id=data_id, contents=data)
        id_packet = self._id_packet(index=new_index, id=data_id)

        self._list[new_index] = data_packet
        self._newest = new_index

        return id_packet

    def get_newest(self):
        """
        get the most recent message on the list
        :return id_packet : (namedtuple->index, id)
        :return contents : (?)
        """

        index = self._newest
        data_id = self._list[index].id

        id_packet = self._id_packet(index=index, id=data_id)
        return id_packet, self._list[index].contents

    def get_oldest(self):
        """
        get the oldest message on the list
        :return id_packet : (namedtuple->index, id)
        :return contents : (?)
        """
        if self._list[-1] is not None:  # if the list is filled until the last element
            index = (self._newest + 1) % self._size
        else:
            index = 1  # index 0 has the initialization message

        try:
            data_id = self._list[index].id
            id_packet = self._id_packet(index=index, id=data_id)
            return id_packet, self._list[index].contents
        except AttributeError:
            raise LookupError('List is empty')

    def get_next(self, id_packet: namedtuple):
        """
        get the message after the given one
        :param id_packet : (namedtuple->index, id)
        :return: id_packet and contents of the next message
        """

        try:
            indexed = self._list[id_packet.index]
        except AttributeError:
            raise LookupError("Provided index does not exist")

        if indexed.id == id_packet.id:
            # all good, still have the referenced data, get the next message
            next_index = (id_packet.index + 1) % self._size

            try:
                next_id = self._list[next_index].id

                if id_packet.id <= next_id:  # the next message is indeed more recent
                    id_packet = self._id_packet(index=next_index, id=next_id)
                    return id_packet, self._list[next_index].contents
                else:
                    print(next_id)
                    raise EOFError('No new data, cool down a bit')

            except AttributeError:  # The list hasn't yet turned over
                raise EOFError('No new data, cool down a bit')
        else:
            raise LookupError('Data has been overwritten, sorry for your loss')

    def get_since(self, id_packet: namedtuple):
        """
        gets all messages since the given one.
        returns the index and date of the latest message and a list with all messages read

        :param id_packet: (namedtuple->index, id)
        :return: id_packet, list of message contents
        """
        messages = []
        try:
            for index in range(self._size):
                id_packet, contents = self.get_next(id_packet)
                messages.append(contents)
        except EOFError:  # end of the list
            if not messages:
                raise EOFError('No new data, cool down a bit')

        return id_packet, messages

    def __str__(self):
        message_contents = []
        for element in self._list:
            try:
                message_contents.append(element.contents)
            except AttributeError:
                message_contents.append(None)

        return message_contents.__str__()
