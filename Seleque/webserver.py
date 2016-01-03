import webapp2


class FakeNameserver:
    def __init__(self):
        self.list_messages = [
            "Gentlemen, you can't fight in here! This is the War Room!",
            "Man who catch fly with chopstick accomplish anything.",
            "If you build it, he will come.",
            "I'm gonna make him an offer he can't refuse.",
            "Life is a box of chocolates, Forrest. You never know what you're gonna get."
        ]

    def message_count(self):
        return len(self.list_messages)

    def messages(self, start_index=-1, end_index=-1):
        if start_index < 0:
            return self.list_messages
        else:
            return self.list_messages[start_index:end_index + 1]


nameserver = FakeNameserver()


class CountHandler(webapp2.RequestHandler):
    def get(self):
        count = nameserver.message_count()
        self.response.write("message count = %d" % (count,))


class MessagesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("<h1>Messages:</h1>")
        for message in nameserver.messages():
            self.response.write("%s<br/>" % (message,))
            # self.response.write("sender %s: %s<br/>" % (message.sender_id, message.text))


class MessagesBlockHandler(webapp2.RequestHandler):
    def get(self, start_index, end_index):
        start_index = int(start_index)
        end_index = int(end_index)

        self.response.write("<h1>Messages from %d to %d:</h1>" % (start_index, end_index))
        for message in nameserver.messages(start_index, end_index):
            self.response.write("%s<br/>" % (message,))
            # self.response.write("sender %s: %s<br/>" % (message.sender_id, message.text))


app = webapp2.WSGIApplication([
    webapp2.Route(r'/count', CountHandler),
    webapp2.Route(r'/messages', MessagesHandler),
    webapp2.Route(r'/messages/<:\d+>/<:\d+>', MessagesBlockHandler)
], debug=True)


def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8080')


if __name__ == '__main__':
    main()
