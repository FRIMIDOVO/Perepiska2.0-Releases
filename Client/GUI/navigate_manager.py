import logging

from Client.core.config import setup_logger


setup_logger()


class NavigateManager:
    def __init__(self, parent):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.parent = parent

        self.page_now = 2

        self.binding()
        self.show_auth_page()

    def binding(self):
        self.parent.open_reg_page_butt.clicked.connect(self.show_reg_page)
        self.parent.open_auth_page_butt.clicked.connect(self.show_auth_page)
        self.parent.open_chat_page_butt.clicked.connect(self.show_chat_page)

    def show_chat_page(self):
        """Переключает на страницу чатов"""
        self.page_now = 0
        self.parent.stackedWidget.setCurrentIndex(0)
        self.parent.users_lst_manager.fill_users_area()
        self.logger.debug('Открыли страницу с чатами')

    def show_reg_page(self):
        """Переключает на страницу логина"""
        self.page_now = 1
        self.parent.stackedWidget.setCurrentIndex(1)
        self.logger.debug('Открыли страницу регистрации')

    def show_auth_page(self):
        self.page_now = 2
        self.parent.stackedWidget.setCurrentIndex(2)
        self.logger.debug('Открыли страницу входа')