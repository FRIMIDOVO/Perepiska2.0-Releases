import logging
import threading

from Server.core.config import setup_logger


setup_logger()


class AdminBash:
    def __init__(self, Handlers):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Handlers = Handlers

        self.commands = {
            '/close_server': self.Handlers.admin_commands.close_server,
            '/users_dict': self.Handlers.admin_commands.users_dict,
            '/help': self.Handlers.admin_commands.help
        }
        self.send_thr = threading.Thread(target=self.send_loop, daemon=True)
        self.send_thr.start()

    def send_loop(self):
        """Цикл чтения админ-команд и их обработки"""
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