import webapp2
from google.appengine.ext import db
import logging


class RegisterServer(db.Model):
    uri = db.StringProperty(required=True)

class RoomToServer(db.Model):
    uri = db.StringProperty(required=True)


class RegisterNewRegisterServer(webapp2.RequestHandler):
    def post(self):
        uri = self.request.get('uri')
        RegisterServer.get_or_insert(key_name=uri, uri=uri).put()


class RegisterRoom(webapp2.RequestHandler):
    def post(self, room_id, uri):
        committed = False
        while not committed:
            try:
                result = self.register_room(room_id, uri)
                committed = True
            except Exception as error:
                logging.info(error)

        self.response.out.write(result)

    @db.transactional
    def register_room(self, room_id, uri):
        if not RoomToServer.get_by_key_name(room_id):
            # store the new uri
            new_rs = RoomToServer(key_name=room_id, uri=uri)
            new_rs.put()

            return 'OK'
        else:
            return 'EXISTS'


class AllServers(webapp2.RequestHandler):
    def get(self):
        all_servers = RegisterServer.all()
        self.response.out.write(all_servers.count())


class JoinRoom(webapp2.RequestHandler):
    def post(self):

        room_id = self.request.get('room')
        entity = RoomToServer.get_by_key_name(room_id)
        if entity:
            self.response.out.write(entity.uri)
        else:
            self.response.out.write('404')


class RemoveRoom(webapp2.RequestHandler):
    def post(self, room_id):
        entity = RoomToServer.get_by_key_name(room_id)
        if entity:
            db.delete(entity)

        self.response.out.write('rs removed')

class ActiveRooms(webapp2.RequestHandler):
    def get(self):
        pass


app = webapp2.WSGIApplication([
    webapp2.Route('/register_rs', handler=RegisterNewRegisterServer),
    webapp2.Route('/register_room', handler=RegisterRoom),
    webapp2.Route('/join_room', handler=JoinRoom),
    webapp2.Route('/remove_room', handler=RemoveRoom),
    webapp2.Route('/all', handler=AllServers),
    webapp2.Route('/active_rooms', handler=ActiveRooms)
], debug=True)
