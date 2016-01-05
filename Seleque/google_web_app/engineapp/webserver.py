import webapp2
from google.appengine.ext import db


class Message(db.Model):
    text = db.StringProperty(required=True)
    author = db.StringProperty(required=True)
    date_time = db.DateTimeProperty(auto_now_add=True)


class AddMessage(webapp2.RequestHandler):
    def get(self):
        text = 'testing'
        author = 'GLaDOS'

        # store the new message
        new_message = Message(text=text, author=author)
        new_message.put()

        self.response.out.write('message added')


class CountHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("message count = %s" % (Message.all().count(),))


class MessagesHandler(webapp2.RequestHandler):
    def get(self):
        messages = db.GqlQuery('SELECT * FROM Message ORDER BY date_time DESC')
        for message in messages:
            self.response.out.write("%s : %s<br/>" % (message.text, message.date_time))


class MessagesBlockHandler(webapp2.RequestHandler):
    def get(self, start_index, end_index):
        start_index = int(start_index)
        end_index = int(end_index)

        messages = db.GqlQuery('SELECT * FROM Message ORDER BY date_time DESC')

        self.response.write("<h1>Messages from %d to %d:</h1>" % (start_index, end_index))
        for message in messages[start_index - 1:end_index]:
            self.response.write("%s : %s<br/>" % (message.text, message.date_time))
            # self.response.write("sender %s: %s<br/>" % (message.sender_id, message.text))


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Welcome to Seleque!')


app = webapp2.WSGIApplication([
    ('/count', CountHandler),
    ('/messages', MessagesHandler),
    webapp2.Route(r'/messages/<:\d+>/<:\d+>', MessagesBlockHandler),
    ('/', MainHandler),
    ('/addmessage', AddMessage)
], debug=True)

