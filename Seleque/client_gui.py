from PyQt4 import QtGui, QtCore
import Pyro4
import threading

from chat_server import Address
from client_design import Ui_MainWindow  # pyuic4 -x file.ui -o output.py
from client import Client, StoppedException
from message import Message


class ClientGui(QtGui.QMainWindow):
    message_signal = QtCore.pyqtSignal(Message)

    def __init__(self, backend):
        super().__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set up the backend communication
        self.backend = backend
        self.receive_thread = ReceiveThread(self.message_signal, self.backend)
        self.message_signal.connect(self.receive_messages)

        # Make some local modifications.
        self.setWindowTitle('Seléque (not in a room)')
        self.ui.message_entry_box.setEnabled(False)
        self.ui.message_entry_box.setText('Not connected to any room')
        self.ui.send_button.setEnabled(False)
        self.ui.message_display_box.setText('')
        self.ui.room_drop_down.clear()
        self.ui.room_drop_down.addItems(sorted(self.backend.get_rooms(), key=str.lower))
        self.ui.room_drop_down.clearEditText()

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
        self.backend.stop()
        super().closeEvent(event)
        sys.exit()

    def leave_room(self):
        self.ui.join_button.setText('Join')
        self.ui.join_button.clicked.disconnect()
        self.ui.join_button.clicked.connect(self.join_room)
        self.ui.message_entry_box.setEnabled(False)
        self.ui.send_button.setEnabled(False)
        self.ui.message_display_box.setText('')
        self.setWindowTitle('Seléque (not in a room)')

        self.backend.leave_room()
        self.nickname = None
        self.room = None

        self.ui.room_drop_down.clear()
        self.ui.room_drop_down.addItems(sorted(self.backend.get_rooms(), key=str.lower))
        self.ui.room_drop_down.clearEditText()
        self.ui.join_button.setEnabled(True)
        self.ui.nickname_box.setEnabled(True)
        self.ui.room_drop_down.setEnabled(True)

    def join_room(self):
        self.nickname = self.ui.nickname_box.text()
        self.room = self.ui.room_drop_down.currentText()
        self.backend.join_room(self.room, self.nickname)
        self.ui.join_button.clicked.disconnect()
        self.ui.join_button.clicked.connect(self.leave_room)
        self.ui.join_button.setText('Leave')

        self.ui.nickname_box.setEnabled(False)
        self.ui.room_drop_down.setEnabled(False)
        self.ui.message_display_box.insertHtml(
                'Joined room: {0}<br>start typing :)<br><br>'.format(self.room))
        self.ui.message_entry_box.setText('')
        self.ui.message_entry_box.setEnabled(True)
        self.ui.send_button.setEnabled(True)
        self.setWindowTitle('Seléque - ' + self.room)
        self.receive_thread.start()

    def send_message(self):
        message = self.ui.message_entry_box.text()
        if message:
            self.ui.message_entry_box.setText('')
            self.backend.send_message(Message(self.backend.id, message))

    def receive_messages(self, message):
        color = 'blue' if message.sender_id == self.backend.id else 'red'
        sender_nickname = self.backend.get_nickname(message.sender_id)
        m = '<font color="{2}">{0}:</font> {1} <br>'.format(sender_nickname,
                                                            message.text, color)
        self.ui.message_display_box.insertHtml(m)
        self.ui.message_display_box.ensureCursorVisible()


class ReceiveThread(QtCore.QThread):
    def __init__(self, signal, backend):
        QtCore.QThread.__init__(self)
        self.new_message = signal
        self.backend = backend

    def run(self):
        while True:
            try:
                message = self.backend.receive_message()
                if message:
                    self.new_message.emit(message)
            except StoppedException:
                break


if __name__ == "__main__":
    import sys

    Pyro4.config.SERIALIZERS_ACCEPTED = ['pickle']
    Pyro4.config.SERIALIZER = 'pickle'

    with open("nameserver_uri.txt") as file:
        name_server_uri = file.readline()

    app = QtGui.QApplication(sys.argv)
    client_gui = ClientGui(Client(name_server_uri))
    client_gui.hide()
    client_gui.show()
    sys.exit(app.exec_())

# todo: backend receive_message should only return when new messages show up
# todo: backend should allow fetching of rooms

