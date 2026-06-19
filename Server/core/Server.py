import logging
from Server.core.config import setup_logger
from Server.managers.client_manager import ClientManager
from Server.handlers.client_handler import ClientHandler
from Server.handlers.client_messages import ClientMessages
from Server.handlers.admin_commands import AdminCommands
from Server.handlers.admin_bash import AdminBash
from Server.managers.auth_manager import AuthManager
from Server.core.server_data_class import Handlers, Managers


setup_logger()


class Server:
    def __init__(self, ip, port):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.addr = (ip, port)

        self.Handlers = Handlers()
        self.Managers = Managers()

        self.admin_commands = AdminCommands(self.Managers)
        self.Handlers.admin_commands = self.admin_commands

        self.admin_bash = AdminBash(self.Handlers)
        self.Handlers.admin_bash = self.admin_bash

        self.auth_manager = AuthManager(self.Managers)
        self.Managers.auth_manager = self.auth_manager

        self.client_messages = ClientMessages(self.Managers)
        self.Handlers.client_messages = self.client_messages

        self.client_handler = ClientHandler(self.addr, self.Handlers, self.Managers)
        self.Handlers.client_handler = self.client_handler

        self.client_manager = ClientManager(self.addr, self.Handlers)
        self.Managers.client_manager = self.client_manager

        self.logger.debug('Все классы инициализированы')
        print('Сервер запущен')