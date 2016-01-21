import webapp2
from google.appengine.ext import db
import logging

class RegisterServer(db.Model):
    #room = db.StringProperty(required=True)
    uri = db.StringProperty(required=True)

class AddRegisterServer(webapp2.RequestHandler):
    def get(self, room_id, uri):
        if not RegisterServer.get_by_key_name(room_id):
        # store the new uri
            new_rs = RegisterServer(key_name = room_id, uri=uri)
            new_rs.put()

            self.response.out.write('rs added')
        else:
            self.response.out.write('failed: already exists')


class SafeAddRegisterServer(webapp2.RequestHandler):
    def get(self, room_id, uri):
        commited = False
        while not commited:
            try:
                result = self.add_register_server(room_id, uri)
                commited = True
            except Exception as error:
                logging.info(error) 

        self.response.out.write(result)            

    @db.transactional
    def add_register_server(self, room_id, uri):
        if not RegisterServer.get_by_key_name(room_id):
        # store the new uri
            new_rs = RegisterServer(key_name = room_id, uri=uri)
            new_rs.put()

            return 'OK'
        else:
            return 'EXISTS'

class SeeRegisterServer(webapp2.RequestHandler):
    def get(self, room_id):
        entity = RegisterServer.get_by_key_name(room_id)
        if entity:
            self.response.out.write(entity.uri)
        else:
            self.response.out.write('404')


class RemRegisterServer(webapp2.RequestHandler):
    def get(self, room_id):
        entity = RegisterServer.get_by_key_name(room_id)
        if entity:
            db.delete(entity)

        self.response.out.write('rs removed')


app = webapp2.WSGIApplication([
    #webapp2.Route('/<room_id>/addrs/<uri>', handler=AddRegisterServer, name='room_id'),
    webapp2.Route('/<room_id>/addrs/<uri>', handler=SafeAddRegisterServer, name='room_id'),
    webapp2.Route('/<room_id>/seers', handler=SeeRegisterServer, name='room_id'),
    webapp2.Route('/<room_id>/remrs', handler=RemRegisterServer, name='room_id')
], debug=True)