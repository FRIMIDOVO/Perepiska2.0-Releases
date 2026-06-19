import logging
from Client.core.config import setup_logger
from Client.core.connector import Connector
from Client.handlers.sender_handler import SenderHandler
from Client.handlers.receiver_handler import ReceiverHandler
from Client.core.client_data_class import Core, Handlers, Managers
from Client.handlers.messages import Messages
from Client.handlers.commands import Commands
from Client.managers.auth_manager import AuthManager


setup_logger()


class Client:
    def __init__(self, ip, port):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.addr = (ip, port)

        self.Core = Core()
        self.Core.addr = self.addr
        self.Handlers = Handlers()
        self.Managers = Managers()

        self.messages = Messages()
        self.Handlers.messages = self.messages

        self.auth_manager = AuthManager(self.Core, self.Handlers)
        self.Managers.auth_manager = self.auth_manager

        self.commands = Commands(self.Core)
        self.Handlers.commands = self.commands

        self.connector = Connector(self.Core)
        self.Core.connector = self.connector

        self.sender_handler = SenderHandler(self.Core, self.Handlers, self.Managers)
        self.Handlers.sender_handler = self.sender_handler

        self.receive_handler = ReceiverHandler(self.Core, self.Handlers)
        self.Handlers.receiver_handler = self.receive_handler

        self.logger.debug('Все классы инициализированы')