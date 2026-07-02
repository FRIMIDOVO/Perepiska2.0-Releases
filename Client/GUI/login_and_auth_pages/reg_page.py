from PyQt5.QtWidgets import QPushButton, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt


import logging

from Client.core.config import setup_logger
from Client.GUI.animations import Animations


setup_logger()


class RegPage(Animations):
    def __init__(self, parent, Protocols):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.parent = parent
        self.Protocols = Protocols

        self.parent.reg_butt.clicked.connect(self.register)
        self.parent.reg_butt.setShortcut(QKeySequence(Qt.Key_Return))

    def register(self):
        if hasattr(self, 'animation'):
            self.animation.stop()

        login = self.parent.reg_login_line.text()
        passw1 = self.parent.reg_password_line.text()
        passw2 = self.parent.reg_password_line_2.text()

        if not login or not passw1 or not passw2:
            self.parent.reg_info_label.setText('Все поля должны быть заполнены')
            self.parent.reg_info_label.setStyleSheet("color: red;")
            self.fade_out_label(self.parent.reg_info_label)
            return

        if passw1 != passw2:
            self.parent.reg_info_label.setText('Пароли не совпадают')
            self.parent.reg_info_label.setStyleSheet("color: red;")
            self.fade_out_label(self.parent.reg_info_label)
            return

        self.Protocols.auth_commands.register(login, passw1)
        self.parent.reg_login_line.clear()
        self.parent.reg_password_line.clear()
        self.parent.reg_password_line_2.clear()