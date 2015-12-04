import webapp2
from webapp2_extras import routes


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('Library main page')


class BooksListHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Books List')


class BookInfoHandler(webapp2.RequestHandler):
    def get(self, book_id):
        self.response.write('Book %s!'% book_id)


class AuthorsListHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Authors List')


class AuthorInfoHandler(webapp2.RequestHandler):
    def get(self, author_id):
        self.response.write('Author %s!'% author_id)


class BooksByAuthorHandler(webapp2.RequestHandler):
    def get(self, author_id):
        self.response.write('Books by Author %s!'% author_id)


app = webapp2.WSGIApplication([
    webapp2.Route(r'/', MainPage),
    webapp2.Route(r'/books', BooksListHandler),
    webapp2.Route(r'/books/<book_id>', BookInfoHandler),
    webapp2.Route(r'/authors', AuthorsListHandler),
    webapp2.Route(r'/authors/<author_id>', AuthorInfoHandler),
    webapp2.Route(r'/authors/<author_id>/books', BooksByAuthorHandler),
], debug=True)


def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8080')

if __name__ == '__main__':
    main()
    

