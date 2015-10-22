class Author:

    def __init__(self):
        self.book_ids = set()

    def insert(self, book_identifier):
        self.book_ids.add(book_identifier)

    def __iter__(self):
        return iter(self.book_ids)
