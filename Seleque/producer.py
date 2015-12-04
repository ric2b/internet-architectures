import Pyro4
import uuid

Pyro4.config.SERIALIZERS_ACCEPTED = 'pickle'
Pyro4.config.SERIALIZER = 'pickle'

uri = input('What is the server uri?')
server = Pyro4.Proxy(uri)

my_id = server.register()
print("My id: ", my_id)

buddy = uuid.UUID(input('buddy: '))

while True:
    msg = input("Message to send: ")
    server.send_message(buddy, msg)
    print('sent')
