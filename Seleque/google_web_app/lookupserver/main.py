import webapp2
from google.appengine.ext import db
import logging


class RegisterServer(db.Model):
    uri = db.StringProperty(required=True)


class Room(db.Model):
    room = db.StringProperty(required=True)


class RegisterRoom(webapp2.RequestHandler):
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
            new_rs = RegisterServer(key_name=room_id, uri=uri)
            new_rs.put()

            return 'OK'
        else:
            return 'EXISTS'


class JoinRoom(webapp2.RequestHandler):
    def get(self, room_id):
        entity = RegisterServer.get_by_key_name(room_id)
        if entity:
            self.response.out.write(entity.uri)
        else:
            self.response.out.write('404')


class RemoveRoom(webapp2.RequestHandler):
    def get(self, room_id):
        entity = RegisterServer.get_by_key_name(room_id)
        if entity:
            db.delete(entity)

        self.response.out.write('rs removed')

class ActiveRooms(webapp2.RequestHandler):
    def get(self):
        pass


app = webapp2.WSGIApplication([
    webapp2.Route('/register_rs/', handler=RegisterServer),
    webapp2.Route('/register_room/', handler=RegisterRoom),
    webapp2.Route('/join_room/', handler=JoinRoom),
    webapp2.Route('/remove_room/', handler=RemoveRoom),
    webapp2.Route('/active_rooms/', handler=ActiveRooms)
], debug=True)
