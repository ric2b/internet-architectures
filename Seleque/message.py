from circular_list import PacketId
from client_id import ClientId


class Message:

    """
    Represents a message exchanged between clients.
    A message has 3 attributes: the sender id, the text of the message, and the message id.
    The message id is given by the server who owns the room to which the message was sent.
    """

    def __init__(self, sender_id: ClientId, text: str, message_id: PacketId = None):
        """
        Initializes the message's attributes. The message must always have a sender id and
        the text. The message id is attributed only by the chat server, which means that
        it may not be specified when the message is created by the client.

        :param sender_id: client id of the sender of the message.
        :param text: text of the message,
        :param message_id: id of the message
        """

        self.sender_id = sender_id
        self.text = text
        self.message_id = message_id

    def __str__(self):
        return "msg(sender=%s, text=%s, id=%s)" % (str(self.sender_id), self.text, str(self.message_id))
