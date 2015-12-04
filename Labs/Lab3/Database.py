import pickle

from Book import Book
from Author import Author


class Database:

    authors = {}
    books = []

    @staticmethod
    def insert_book(author, title, pub_date):
        new_book = Book(author, title, pub_date)
        Database.books.append(new_book)

        if author not in Database.authors:
            Database.authors[author] = Author()

        Database.authors[author].insert(new_book.identifier)

        with open("Database Book Backup", "wb") as database_book_backup:
            pickle.dump(Database.books, database_book_backup)

        with open("Database Author Backup", "wb") as database_author_backup:
            pickle.dump(Database.books, database_author_backup)

    @staticmethod
    def show_book(identifier):
        try:
            print(Database.books[identifier])
        except IndexError:
            print("Invalid book identifier")

    @staticmethod
    def get_books_by(author):
        try:
            for book in Database.authors[author]:
                print(Database.books[book])
                print("-----------")

        except KeyError:
            print("Author \'" + author + "\' isn't in the database")
