import logging
import threading

from Server.core.config import setup_logger


setup_logger()


class AdminBash:
    def __init__(self, Protocols):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Protocols = Protocols

        self.commands = {
            '/close_server': self.Protocols.admin_commands.close_server,
            '/users': self.Protocols.admin_commands.users_dict,
            '/help': self.Protocols.admin_commands.help
        }
        self.send_thr = threading.Thread(target=self.send_loop, daemon=True)
        self.send_thr.start()

    def send_loop(self):
        """Цикл чтения админ-команд и их обработки"""
        while True:
            try:
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
            except:
                self.Protocols.admin_commands.close_server(None)