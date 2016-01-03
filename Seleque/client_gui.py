from PyQt4 import QtGui
import Pyro4
import threading

from chat_server import Address
from client_design import Ui_MainWindow
from client import Client


class ClientGui:
    def __init__(self, main_window, backend):

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(main_window)

        # Set up the backend communication
        self.backend = backend

        # Make some local modifications.
        self.ui.message_entry_box.setEnabled(False)
        self.ui.message_entry_box.setText('Not connected to any room')
        self.ui.send_button.setEnabled(False)
        self.ui.message_display_box.setText('')

        # Connect up the buttons.
        self.ui.join_button.clicked.connect(self.join_room)
        self.ui.send_button.clicked.connect(self.send_message)

        # Set variables
        self.in_room = False

    def join_room(self):
        nickname = self.ui.nickname_box.text()
        room = self.ui.room_drop_down.currentText()
        self.backend.join_room(room, nickname)
        self.ui.message_display_box.setText('Joined room: {0}\nstart typing :)'.format(room))
        self.ui.message_entry_box.setText('')
        self.ui.message_entry_box.setEnabled(True)
        self.ui.send_button.setEnabled(True)
        self.in_room = True
        threading.Thread(target=self.receive_messages).start()

    def send_message(self):
        message = self.ui.message_entry_box.text()
        self.backend.send_message(message)

    def receive_messages(self):
        while True:
            for author, message in self.backend.receive_message():
                self.ui.message_display_box.append('{0}: {1}'.format(author, message))

if __name__ == "__main__":
    import sys

    Pyro4.config.SERIALIZERS_ACCEPTED = 'pickle'
    Pyro4.config.SERIALIZER = 'pickle'

    name_server_uri = 'PYRO:name_server@localhost:63669'

    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    client = ClientGui(MainWindow, Client(name_server_uri))
    MainWindow.show()

    sys.exit(app.exec_())
