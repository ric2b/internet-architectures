from Lab3.Database import Database as Db


class Client:

    @staticmethod
    def new(author, title, pub_date):
        Db.insert_book(author, title, pub_date)

    @staticmethod
    def show(identifier):
        Db.show_book(identifier)

    @staticmethod
    def list(author):
        Db.get_books_by(author)
