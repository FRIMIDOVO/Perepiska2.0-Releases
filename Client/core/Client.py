import logging

from Client.core.client_data_classes import Core, Handlers, Protocols
from Client.core.config import setup_logger
from Client.core.connector import Connector

from Client.handlers.receiver_handler import ReceiverHandler
from Client.handlers.sender_handler import SenderHandler

from Client.Protocols.auth_commands import AuthCommands
from Client.Protocols.file_commands import FileCommands
from Client.Protocols.commands import Commands
from Client.Protocols.messages import Messages


setup_logger()


class Client:
    def __init__(self, ip, port):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.addr = (ip, port)

        self.Core = Core(); self.Core.addr = self.addr
        self.Handlers = Handlers()
        self.Protocols = Protocols()

        self.messages = Messages(self.Protocols)
        self.Protocols.messages = self.messages

        self.auth_commands = AuthCommands(self.Core, self.Handlers)
        self.Protocols.auth_commands = self.auth_commands

        self.file_commands = FileCommands(self.Core)
        self.Protocols.file_commands = self.file_commands

        self.commands = Commands(self.Core, self.Protocols)
        self.Protocols.commands = self.commands

        self.connector = Connector(self.Core)
        self.Core.connector = self.connector

        self.sender_handler = SenderHandler(self.Core, self.Protocols)
        self.Handlers.sender_handler = self.sender_handler

        self.receiver_handler = ReceiverHandler(self.Core, self.Protocols)
        self.Handlers.receiver_handler = self.receiver_handler

        self.logger.debug('Все классы инициализированы')