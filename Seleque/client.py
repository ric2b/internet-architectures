import Pyro4

Pyro4.config.SERIALIZERS_ACCEPTED = 'pickle'
Pyro4.config.SERIALIZER = 'pickle'

uri = input('What is the server uri?')
server = Pyro4.Proxy(uri)

my_id = server.register()
print("My id: ", my_id)

while True:
    try:
        print('received: ', server.receive_message(my_id))
    except Exception:
        print("Pyro traceback:")
        print("".join(Pyro4.util.getPyroTraceback()))
        exit()
