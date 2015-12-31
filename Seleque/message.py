from circular_list import PacketId
from client_id import ClientId


class Message:

    """
    Represents a message exchanged between clients.
    A message has 2 attributes: the sender id, and the text of the message.
    """

    def __init__(self, sender_id: ClientId, text: str):
        """
        Initializes the message's attributes. The message must always have a sender id and
        the text.

        :param sender_id: client id of the sender of the message.
        :param text: text of the message,
        """

        self.sender_id = sender_id
        self.text = text

    def __str__(self):
        return "msg(sender=%s, text=%s)" % (str(self.sender_id), self.text)
