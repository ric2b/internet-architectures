import webapp2
from webapp2_extras import routes

import Lab6.library as library


bd = library.Library("mylib")


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('Library main page')


class BooksListHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(bd.list_books())


class NewBookHandler(webapp2.RequestHandler):
    def get(self):
        f = open('new.html', 'r')
        self.response.write(f.read())
        f.close()

    def post(self):
        author = self.request.get('author')
        title = self.request.get('title')
        year = self.request.get('year')
        bd.add_book(author, title, year)
        self.response.write("book \'{}\' by author \'{}\' was added".format(title, author))


class AuthorListHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(bd.list_authors())


class GetBookHandler(webapp2.RequestHandler):
    def get(self, book_id):
        book = bd.get_book(int(book_id))
        if book == {}:
            self.response.status = '404 Not Found'
            self.response.write("The book id {} wasn't found in the database".format(book_id))
        else:
            self.response.write(book)


class GetAuthorHandler(webapp2.RequestHandler):
    def get(self, author_name):
        self.response.write(bd.list_books(author_name))

app = webapp2.WSGIApplication([
    webapp2.Route(r'/', MainPage),
    webapp2.Route(r'/newbook', NewBookHandler),
    webapp2.Route(r'/books', BooksListHandler),
    webapp2.Route(r'/authors', AuthorListHandler),
    webapp2.Route(r'/books/<book_id:\d+>', GetBookHandler),
    webapp2.Route(r'/authors/<author_name>', GetAuthorHandler),
], debug=True)


def main():
    from paste import httpserver
    httpserver.serve(app, host='193.136.131.16', port='8080')

if __name__ == '__main__':
    main()
    

