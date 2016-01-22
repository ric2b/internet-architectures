import random

import webapp2
from google.appengine.ext import db
import logging


class RegisterServer(db.Model):
    uri = db.StringProperty(required=True)

class RoomToServer(db.Model):
    uri = db.StringProperty(required=True)
    http_address = db.StringProperty(required=True)


class RegisterNewRegisterServer(webapp2.RequestHandler):
    def post(self):
        uri = self.request.get('uri')
        RegisterServer.get_or_insert(key_name=uri, uri=uri).put()


class RegisterRoom(webapp2.RequestHandler):
    def post(self):
        room_id = self.request.get('room_id')
        uri = self.request.get('uri')
        http_address = self.request.get('http_address')

        committed = False
        while not committed:
            try:
                result = self.register_room(room_id, uri, http_address)
                committed = True
            except Exception as error:
                logging.info(error)

        self.response.out.write(result)

    @db.transactional
    def register_room(self, room_id, uri, http_address):
        if not RoomToServer.get_by_key_name(room_id):
            # store the new uri
            new_rs = RoomToServer(key_name=room_id, uri=uri, http_address=http_address)
            new_rs.put()

            return 'OK'
        else:
            return 'EXISTS'


class AllServers(webapp2.RequestHandler):
    def get(self):
        all_servers = RegisterServer.all()
        for server in all_servers:
            self.response.out.write(server.key().name() + '\n')


class JoinRoom(webapp2.RequestHandler):
    def post(self):

        room_id = self.request.get('room_id')
        entity = RoomToServer.get_by_key_name(room_id)
        if entity:
            self.response.out.write(entity.uri)
        else:
            server = get_random_register_server()
            self.response.out.write(server.key().name())


class GiveMeTheRoomRegisterServer(webapp2.RequestHandler):
    def get(self, room_id):
        entity = RoomToServer.get_by_key_name(room_id)
        if entity:
            self.response.out.write(entity.http_address)
        else:
            self.response.out.write('')


class RemoveRoom(webapp2.RequestHandler):
    def post(self):
        room_id = self.request.get('room_id')
        entity = RoomToServer.get_by_key_name(room_id)
        if entity:
            db.delete(entity)

        self.response.out.write('rs removed')


def get_random_register_server():
    all_servers = RegisterServer.all()
    server_index = random.randrange(0, all_servers.count())
    return all_servers[server_index]


class ActiveRooms(webapp2.RequestHandler):
    def get(self):
        rooms = RoomToServer.all(keys_only=True)
        room_ids = [room.name() for room in rooms]
        formated = '\n'.join(room_ids)
        self.response.write(formated)


app = webapp2.WSGIApplication([
    webapp2.Route('/register_rs', handler=RegisterNewRegisterServer),
    webapp2.Route('/register_room', handler=RegisterRoom),
    webapp2.Route('/join_room', handler=JoinRoom),
    webapp2.Route('/givemetheroomregisterserver/<room_id>', handler=GiveMeTheRoomRegisterServer),
    webapp2.Route('/remove_room', handler=RemoveRoom),
    webapp2.Route('/all', handler=AllServers),
    webapp2.Route('/active_rooms', handler=ActiveRooms)
], debug=True)
