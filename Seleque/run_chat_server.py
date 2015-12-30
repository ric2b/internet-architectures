import socket

from chat_server import ChatServer, Address

if __name__ == "__main__":

    server = ChatServer(Address(socket.gethostname(), socket.htons(5000)), 10)
    print(server.uri)
    server.start_loop()
