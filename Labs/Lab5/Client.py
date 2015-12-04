import threading
import time


count = 0
# Define a function for the thread


def loop1():
    global count

    while True:
        count = int(input(""))


def loop2():
    global count

    while True:

        time.sleep(0.5)
        count += 1
        print("%d" % count)

threading.Thread(None, loop1, ()).start()

loop2()
