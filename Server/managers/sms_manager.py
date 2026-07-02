import logging
from collections import defaultdict

from Server.core.config import setup_logger
from Server.core.json_protocol import JsonProtocol


setup_logger()


class SmsManager(JsonProtocol):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.sms_path = 'data/sms.json'
        data = self.load_from_file(self.sms_path)
        self.sms = defaultdict(list, data) # {user: [{}, {}, ...], user2: [...], ...}

        self.logger.debug('Инициализирован')

    def add_message(self, username, data):
        """Добавляет сообщение юзеру в офлайн очередь"""
        self.sms[username].append(data)
        self.save_to_file(self.sms_path, self.sms)

    def deliver_all_messages(self, username, client_socket):
        if username not in self.sms.keys():
            return
        count = len(self.sms[username])
        for data in self.sms.get(username):
            try:
                client_socket.send(self.encode(data))
            except Exception as err:
                self.logger.error(f'Ошибка отправки офлайн-сообщения: {err}')
        del self.sms[username]
        self.save_to_file(self.sms_path, self.sms)
        self.logger.info(f'Доставлено {count} офлайн-сообщений для {username}')