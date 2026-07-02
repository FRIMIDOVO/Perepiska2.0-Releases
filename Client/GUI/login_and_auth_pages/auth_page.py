from PyQt5.QtWidgets import QPushButton, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

import logging

from Client.core.config import setup_logger
from Client.GUI.animations import Animations


setup_logger()


class AuthPage(Animations):
    def __init__(self, parent, Protocols):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.parent = parent
        self.Protocols = Protocols

        self.parent.auth_butt.clicked.connect(self.auth)
        self.parent.auth_butt.setShortcut(QKeySequence(Qt.Key_Return))

    def auth(self):
        login = self.parent.auth_login_line.text()
        passw = self.parent.auth_password_line.text()

        if not login or not passw:
            self.parent.auth_info_label.setText('Все поля должны быть заполнены')
            self.parent.auth_info_label.setStyleSheet("color: red;")
            self.fade_out_label(self.parent.auth_info_label)
            return
        self.Protocols.auth_commands.auth(login, passw)
        self.parent.auth_login_line.clear()
        self.parent.auth_password_line.clear()