from datetime import datetime

import webapp2
from google.appengine.ext import db
import counters as counters
from google.appengine.ext.webapp import template


def get_room_messages(room_id, start_date=None, end_date=None):
    """
    Retrieves the all the messages in a room.

    :param room_id: id of the room to get the messages from.
    :param start_date:
    :param end_date:
    :return: list with the messages.
    :raises AttributeError: if given room id does not exist.
    """
    room = Room.get_by_key_name([room_id])[0]
    if room is None:
        raise AttributeError("room '%s' does not exist", (room_id,))

    messages = db.GqlQuery("SELECT * FROM Message "
                           "WHERE ANCESTOR is :room "
                           "AND date_time >= DATETIME(:start_year, :start_month, :start_day, 0, 0, 0)"
                           "AND date_time <= DATETIME(:end_year, :end_month, :end_day, 23, 59, 59)"
                           "ORDER BY date_time DESC",
                           room=room.key(),
                           start_year=start_date.year, start_month=start_date.month, start_day=start_date.day,
                           end_year=end_date.year, end_month=end_date.month, end_day=end_date.day)

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
    nickname = db.StringProperty(required=True)
    date_time = db.DateTimeProperty(auto_now_add=True)


class AddMessage(webapp2.RequestHandler):
    def get(self, room_id):
        text = 'testing'
        author = 'GLaDOS'

        room = Room.get_or_insert(room_id)

        # store the new message
        new_message = Message(text=text, author=author, nickname=author, parent=room)
        new_message.put()

        counters.increment(room_id)
        self.response.out.write('message added')

    def post(self, room_id):
        sender_id = str(self.request.get('sender_id'))
        nickname = str(self.request.get('nickname'))
        text = str(self.request.get('text'))

        room = Room.get_or_insert(room_id)

        new_message = Message(text=text, author=sender_id, nickname=nickname, parent=room)
        new_message.put()
        counters.increment(room_id)


class CountHandler(webapp2.RequestHandler):
    def get(self, room_id):
        if Room.get_by_key_name([room_id])[0]:
            self.response.write("message count = %s" % (counters.get_count(room_id),))    
        else:
            not_found_room(self.response, room_id)        


class MessagesHandler(webapp2.RequestHandler):
    def get(self, room_id):
        self.response.write(template.render('messages.html', {}))

    def post(self, room_id):
        start_date = str(self.request.get('start_date'))
        end_date = str(self.request.get('end_date'))

        if not start_date:
            start_date = datetime(1, 1, 1, 0, 0, 0)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        try:
            messages = get_room_messages(room_id, start_date, end_date)
            self.response.write("<h1>Messages from %s to %s:</h1>" % (start_date.date(), end_date.date()))
            for message in messages:
                self.response.write("%s : %s<br/>" % (message.text, message.date_time))
                # self.response.write("sender %s: %s<br/>" % (message.sender_id, message.text))
        except AttributeError:
            not_found_room(self.response, room_id)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(template.render('index.html', {}))

app = webapp2.WSGIApplication([
    webapp2.Route('/<room_id>/messagecount', handler=CountHandler, name='room_id'),
    webapp2.Route('/<room_id>/messages', handler=MessagesHandler, name='room_id'),
    ('/', MainHandler),
    webapp2.Route('/<room_id>/addmessage', handler=AddMessage, name='room_id')
], debug=True)
