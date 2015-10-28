# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 10:02:24 2014

@author: jnos
"""
import pickle

import Lab6.book as book


class Library:
    def __init__(self, name):
        self.name = name
        try:
            f = open('bd_dump'+name, 'rb')
            self.bib = pickle.load(f)
            f.close()

        except IOError:
            self.bib = {}

    def add_book(self, author, title, year):
        b_id = len(self.bib)
        self.bib[b_id] = book.book(author, title, year, b_id)
        f = open('bd_dump'+self.name, 'wb')
        pickle.dump(self.bib, f)
        f.close()

    def get_book(self, b_id):
        try:
            b = self.bib[b_id]
            return {'id': b.id, 'author': b.author, 'title': b.title, 'date':b.year, 'votes': b.sum_votes}
        except:
            return {}
        pass

    def list_authors(self):
        authors = {}
        for b in self.bib.values():
            authors[b.author] = 1

        return {'authors': authors.keys()}

    def list_books(self, name=''):
        ret_value = []

        if name =='':
            for b in self.bib.values():
                ret_value.append({'id': b.id, 'author': b.author, 'title': b.title, 'date':b.year, 'votes': b.sum_votes} )
        else:
            for b in self.bib.values():
                if b.author == name:
                    ret_value.append({'id': b.id, 'author': b.author, 'title': b.title, 'date':b.year, 'votes': b.sum_votes} )
        return {'books': ret_value}

    def search_book(self, b_id):
        return self.bib[b_id]
