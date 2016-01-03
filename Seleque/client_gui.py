from PyQt4 import QtGui
import Pyro4
import threading

from chat_server import Address
from client_design import Ui_MainWindow  # pyuic4 -x file.ui -o output.py
from client import Client


class ClientGui(QtGui.QMainWindow):
    def __init__(self, backend):
        super().__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set up the backend communication
        self.backend = backend

        # Make some local modifications.
        self.setWindowTitle('Seléque (not in a room)')
        self.ui.message_entry_box.setEnabled(False)
        self.ui.message_entry_box.setText('Not connected to any room')
        self.ui.send_button.setEnabled(False)
        self.ui.message_display_box.setText('')

        # Connect up the buttons.
        self.ui.join_button.clicked.connect(self.join_room)
        self.ui.join_button.setAutoDefault(True)
        self.ui.send_button.clicked.connect(self.send_message)
        self.ui.send_button.setAutoDefault(True)
        self.ui.message_entry_box.returnPressed.connect(self.send_message)

        # Set variables
        self.room = None
        self.nickname = None

    def closeEvent(self, event):
        self.leave_room()
        super().closeEvent(event)

    def leave_room(self):
        # todo: add a leave room method to the client backend
        # self.backend.leave_room()
        pass

    def join_room(self):
        if self.room:
            self.leave_room()

        self.nickname = self.ui.nickname_box.text()
        self.room = self.ui.room_drop_down.currentText()
        self.backend.join_room(self.room, self.nickname)
        self.ui.message_display_box.insertHtml('Joined room: {0}<br>start typing :)<br><br>'.format(self.room))
        self.ui.message_entry_box.setText('')
        self.ui.message_entry_box.setEnabled(True)
        self.ui.send_button.setEnabled(True)
        self.setWindowTitle('Seléque - ' + self.room)
        threading.Thread(target=self.receive_messages).start()

    def send_message(self):
        message = self.ui.message_entry_box.text()
        if message:
            self.ui.message_entry_box.setText('')
            self.backend.send_message(message)

    def receive_messages(self):
        while self.room:
            for author, message in self.backend.receive_message():
                color = 'blue' if author == self.nickname else 'red'
                m = '<font color="{2}">{0}:</font> {1} <br>'.format(author, message, color)
                self.ui.message_display_box.insertHtml(m)

if __name__ == "__main__":
    import sys

    Pyro4.config.SERIALIZERS_ACCEPTED = 'pickle'
    Pyro4.config.SERIALIZER = 'pickle'

    name_server_uri = 'PYRO:name_server@localhost:52913'

    app = QtGui.QApplication(sys.argv)
    client_gui = ClientGui(Client(name_server_uri))
    client_gui.hide()
    client_gui.show()
    sys.exit(app.exec_())

# todo: backend receive_message should only return when new messages show up

