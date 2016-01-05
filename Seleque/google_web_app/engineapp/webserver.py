import webapp2
from google.appengine.ext import db


def get_room_messages(room_id):
    """
    Retrieves the all the messages in a room.

    :param room_id: id of the room to get the messages from.
    :return: list with the messages.
    :raises AttributeError: if given room id does not exist.
    """
    room_key = db.Key.from_path('Room', room_id)
    messages = db.GqlQuery("SELECT * FROM Message WHERE ANCESTOR is :1 ORDER BY date_time DESC", room_key)

    if messages.count(limit=1) == 0:
        raise AttributeError("room '%s' does not exist", (room_id,))

    return messages


def not_found_room(response, room_id):
    """ Prints a not found message for the given room """
    response.status = '404 Not Found'
    response.write("404 Not Found {}".format(room_id))


class Room(db.Model):
    pass


class Message(db.Model):
    text = db.StringProperty(required=True)
    author = db.StringProperty(required=True)
    date_time = db.DateTimeProperty(auto_now_add=True)


class AddMessage(webapp2.RequestHandler):
    def get(self, room_id):
        text = 'testing'
        author = 'GLaDOS'

        room = Room.get_or_insert(room_id)

        # store the new message
        new_message = Message(text=text, author=author, parent=room)
        new_message.put()

        self.response.out.write('message added')


class CountHandler(webapp2.RequestHandler):
    def get(self, room_id):
        try:
            self.response.write("message count = %s" % (get_room_messages(room_id).count(),))
        except AttributeError:
            not_found_room(self.response, room_id)


class MessagesHandler(webapp2.RequestHandler):
    def get(self, room_id):
        try:
            messages = get_room_messages(room_id)
            for message in messages:
                self.response.out.write("%s : %s<br/>" % (message.text, message.date_time))
        except AttributeError:
            not_found_room(self.response, room_id)


class MessagesBlockHandler(webapp2.RequestHandler):
    def get(self, room_id, start_index, end_index):
        start_index = int(start_index)
        end_index = int(end_index)

        try:
            messages = get_room_messages(room_id)

            self.response.write("<h1>Messages from %d to %d:</h1>" % (start_index, end_index))
            for message in messages[start_index - 1:end_index]:
                self.response.write("%s : %s<br/>" % (message.text, message.date_time))
                # self.response.write("sender %s: %s<br/>" % (message.sender_id, message.text))
        except AttributeError:
            not_found_room(self.response, room_id)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Welcome to Seleque!')


app = webapp2.WSGIApplication([
    webapp2.Route('/<room_id>/count', handler=CountHandler, name='room_id'),
    webapp2.Route('/<room_id>/messages', handler=MessagesHandler, name='room_id'),
    webapp2.Route('/<room_id>/messages/<:\d+>/<:\d+>', handler=MessagesBlockHandler),
    ('/', MainHandler),
    webapp2.Route('/<room_id>/addmessage', handler=AddMessage, name='room_id')
], debug=True)

