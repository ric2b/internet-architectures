import threading

from client import Client


def user_input(client):
    while True:
        message = input("Write a message:")
        client.send_message(message)


def main():
    client = Client()
    client.register("PYRO:server@localhost:47216")

    threading.Thread(target=user_input, args=[client]).start()

    while True:
        message = client.receive_message()
        print("\n%s" % (message,))

if __name__ == "__main__":
    main()
