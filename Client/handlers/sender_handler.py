import threading
import logging

from Client.core.config import setup_logger


setup_logger()


class SenderHandler:
    def __init__(self, Core, Protocols):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Core = Core; self.addr = self.Core.addr
        self.Protocols = Protocols

        self.commands = {
            '/msg': self.Protocols.commands.private_message,
            '/set_nick': self.Protocols.commands.set_nickname,
            '/help': self.Protocols.commands.help,
            '/offline_sms': self.Protocols.commands.get_offline_sms,
            '/all_files': self.Protocols.commands.all_files,
            '/auth': self.Protocols.auth_commands.auth,
            '/send_file': self.Protocols.file_commands.send_file,
            '/load_file': self.Protocols.commands.load_file,
            '/exit': self.Protocols.commands.exit
        }
        self.send_thr = threading.Thread(target=self.send_loop, daemon=True)
        self.send_thr.start()
        self.logger.debug('Инициализирован')

    def send_loop(self):
        """Цикл чтения команд и их обработки"""
        while True:
            try:
                text = input()
                if not text:
                    continue
                parts = text.split(maxsplit=1)
                command = parts[0]
                if command not in self.commands:
                    print(f'Команды "{command}" не существует. /help для справки')
                    continue
                arg = parts[1] if len(parts) > 1 else ""
                self.commands[command](arg)
            except:
                self.Protocols.commands.exit(None)