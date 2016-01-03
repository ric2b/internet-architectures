# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client_design.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(450, 500)
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.join_button = QtGui.QPushButton(self.centralwidget)
        self.join_button.setObjectName(_fromUtf8("join_button"))
        self.gridLayout.addWidget(self.join_button, 1, 4, 1, 1)
        self.message_display_box = QtGui.QTextBrowser(self.centralwidget)
        self.message_display_box.setObjectName(_fromUtf8("message_display_box"))
        self.gridLayout.addWidget(self.message_display_box, 5, 1, 1, 4)
        self.nickname_box = QtGui.QLineEdit(self.centralwidget)
        self.nickname_box.setObjectName(_fromUtf8("nickname_box"))
        self.gridLayout.addWidget(self.nickname_box, 1, 1, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.message_entry_box = QtGui.QLineEdit(self.centralwidget)
        self.message_entry_box.setObjectName(_fromUtf8("message_entry_box"))
        self.horizontalLayout_2.addWidget(self.message_entry_box)
        self.send_button = QtGui.QPushButton(self.centralwidget)
        self.send_button.setObjectName(_fromUtf8("send_button"))
        self.horizontalLayout_2.addWidget(self.send_button)
        self.gridLayout.addLayout(self.horizontalLayout_2, 7, 1, 1, 4)
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 1, 1, 1)
        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 2, 1, 2, 4)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 2, 1, 1)
        self.room_drop_down = QtGui.QComboBox(self.centralwidget)
        self.room_drop_down.setEnabled(True)
        self.room_drop_down.setEditable(True)
        self.room_drop_down.setObjectName(_fromUtf8("room_drop_down"))
        self.gridLayout.addWidget(self.room_drop_down, 1, 2, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 450, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.nickname_box, self.room_drop_down)
        MainWindow.setTabOrder(self.room_drop_down, self.join_button)
        MainWindow.setTabOrder(self.join_button, self.message_entry_box)
        MainWindow.setTabOrder(self.message_entry_box, self.send_button)
        MainWindow.setTabOrder(self.send_button, self.message_display_box)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Seléque", None))
        self.join_button.setText(_translate("MainWindow", "Join", None))
        self.message_display_box.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Hello</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">this is a test</span></p></body></html>", None))
        self.message_entry_box.setText(_translate("MainWindow", "My message", None))
        self.send_button.setText(_translate("MainWindow", "Send", None))
        self.label_3.setText(_translate("MainWindow", "Choose a nickname:", None))
        self.label.setText(_translate("MainWindow", "Create a room or choose an existing one: ", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

