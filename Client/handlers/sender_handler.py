import threading
import logging
from Client.core.config import setup_logger


setup_logger()


class SenderHandler:
    def __init__(self, Core, Handlers, Managers):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Core = Core
        self.addr = self.Core.addr
        self.Handlers = Handlers
        self.Managers = Managers

        self.commands = {
            '/msg': self.Handlers.commands.private_message,
            '/set_nick': self.Handlers.commands.set_nickname,
            '/help': self.Handlers.commands.help,
            '/get_users': self.Handlers.commands.get_users_list,
            '/reg': self.Managers.auth_manager.register,
            '/auth': self.Managers.auth_manager.auth,
            '/exit': self.Handlers.commands.exit
        }
        self.send_thr = threading.Thread(target=self.send_loop, daemon=True)
        self.send_thr.start()
        self.logger.debug('Инициализирован')

    def send_loop(self):
        """Цикл чтения команд и их обработки"""
        while True:
            text = input()
            if not text:
                continue
            parts = text.split(maxsplit=1)
            command = parts[0]
            if command not in self.commands:
                print(f'Команды "{command}" не существует. /help для помощи')
                continue
            arg = parts[1] if len(parts) > 1 else ""
            self.commands[command](arg)