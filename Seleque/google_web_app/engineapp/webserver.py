import webapp2
from google.appengine.ext import db
from google.appengine.ext import ndb

import counters as counters


def get_room_messages(room_id):
    """
    Retrieves the all the messages in a room.

    :param room_id: id of the room to get the messages from.
    :return: list with the messages.
    :raises AttributeError: if given room id does not exist.
    """
    room = Room.get_by_key_name([room_id])[0]
    if room is None:
        raise AttributeError("room '%s' does not exist", (room_id,))

    return Message.all().ancestor(room)


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

        counters.increment(room_id)
        self.response.out.write('message added')


class CountHandler(webapp2.RequestHandler):
    def get(self, room_id):
        if Room.get_by_key_name([room_id])[0]:
            self.response.write("message count = %s" % (counters.get_count(room_id),))    
        else:
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

        self.response.write("<h1>Messages from %d to %d:</h1>" % (start_index, end_index))
        try:
            messages = get_room_messages(room_id)
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
    webapp2.Route(r'/<room_id>/messages/<:\d+>/<:\d+>', handler=MessagesBlockHandler, name='room_id'),
    ('/', MainHandler),
    webapp2.Route('/<room_id>/addmessage', handler=AddMessage, name='room_id')
], debug=True)
