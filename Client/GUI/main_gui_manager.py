import sys

from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtWidgets import QVBoxLayout, QSpacerItem, QSizePolicy

from Client.GUI.designs.main_window_design import Ui_MainWindow
from Client.GUI.navigate_manager import NavigateManager
from Client.GUI.login_and_auth_pages.reg_page import RegPage
from Client.GUI.login_and_auth_pages.auth_page import AuthPage
from Client.GUI.user_chats_page.users_lst_manager import UsersLst
from Client.GUI.user_chats_page.chat_area_manager import ChatArea
from Client.GUI.toast import Toast
from Client.core.config import setup_logger

import logging


setup_logger()


class GuiManager(QMainWindow, Ui_MainWindow):
    def __init__(self, Core, Protocols):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Core = Core
        self.Protocols = Protocols

        # Настройка основного окна
        self.setupUi(self)
        self.retranslateUi(self)

        # Создаем менеджеры страниц
        self.navigate_manager = NavigateManager(self)
        self.reg_manager = RegPage(self, self.Protocols)
        self.auth_manager = AuthPage(self, self.Protocols)
        self.users_lst_manager = UsersLst(self, self.Protocols)
        self.chat_area_manager = ChatArea(self, self.Protocols)

        # ПОДКЛЮЧАЕМ СИГНАЛЫ
        self.Core.connector.connection_lost.connect(lambda msg: self._msg(msg, 'error'))
        self.Protocols.messages.error_msg.connect(lambda msg: self._msg(msg, 'error'))
        self.Protocols.messages.info_msg.connect(lambda msg: self._msg(msg, 'info'))

        self.logger.debug('GUI инициализирован')

    def _msg(self, message, type):
        match self.navigate_manager.page_now:
            case 0:
                Toast(message, type, self.messages_scrollArea)
            case _:
                Toast(message, type, self)