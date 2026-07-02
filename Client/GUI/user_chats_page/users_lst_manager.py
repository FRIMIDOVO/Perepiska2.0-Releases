import logging

from Client.core.config import setup_logger

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from Client.GUI.designs.us_wid import Ui_us_wid

setup_logger()


class UserWidgetItem(QWidget):
    """Виджет для одного пользователя, на основе us_wid.ui"""
    def __init__(self, name, is_online=False, parent=None):
        super().__init__(parent)

        self.ui = Ui_us_wid()
        self.ui.setupUi(self)
        self.setMinimumHeight(75)

        self.ui.open_chat_with_us_butt.setText(name)

        color = "green" if is_online else "gray"
        self.ui.status_us.setStyleSheet(f"background-color: {color};")


class UsersLst:
    def __init__(self, parent, Protocols):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.parent = parent
        self.Protocols = Protocols

        # Создаем лейаут для внутреннего виджета
        self.users_layout = QVBoxLayout(self.parent.users_scrollArea_wid)
        self.users_layout.setAlignment(Qt.AlignTop)

        # Убираем лишние отступы
        self.users_layout.setContentsMargins(0, 0, 0, 0)
        self.users_layout.setSpacing(0)

    def add_user_wid(self, name, is_online):
        """Добавляет в область виджет для одного из юзеров"""
        user_widget = UserWidgetItem(name, is_online)
        self.users_layout.addWidget(user_widget)

    def fill_users_area(self):
        """Заполняет область с юзерами"""
        self.Protocols.commands.get_users_list()
        users_data = self.Protocols.messages._get_answer('return_users_list', timeout=0.2)
        if not users_data:
            self.logger.error('Превышено время ожидания сервера')
            return
        self._clear_users_layout()
        for us_data in users_data.get('list'):
            nickname = us_data.get('nickname')
            is_online = us_data.get('online')
            self.add_user_wid(nickname, is_online)

    def _clear_users_layout(self):
        while item := self.users_layout.takeAt(0):
            if widget := item.widget():
                widget.deleteLater()