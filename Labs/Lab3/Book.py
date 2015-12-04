class Book:

    counter = 0

    def __init__(self, author, title, pub_date):
        self.author = author
        self.title = title
        self.pub_date = pub_date
        self.identifier = Book.counter

        Book.counter += 1

    def __repr__(self):
        return "Author: " + self.author + '\n' "Title: " + self.title + '\n' + "Publication Date: " + str(self.pub_date)
