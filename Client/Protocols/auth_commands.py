import logging
import base64, hashlib

from Client.core.config import setup_logger, check_connection, debug_log
from Client.core.json_protocol import JsonProtocol


setup_logger()


class AuthCommands(JsonProtocol):
    def __init__(self, Core, Handlers):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Core = Core
        self.Handlers = Handlers
        self.logger.debug('Инициализирован')

    @check_connection()
    @debug_log # /reg <username> <password> <password>
    def register(self, text):
        """Запрос на регистрацию"""
        parts = text.split()
        if len(parts) != 3:
            print('Правильное использование: /reg <юзернейм> <пароль> <пароль>')
            return
        if parts[1] != parts[2]:
            print('Пароли не совпадают!')
            return
        salt = self._get_salt(parts[0])
        if not salt:
            return
        salt_bytes = base64.b64decode(salt.encode('utf-8'))
        hash_pwd = hashlib.pbkdf2_hmac('sha256', parts[1].encode(), salt_bytes, 100000)
        hash_b64 = base64.b64encode(hash_pwd).decode('utf-8')
        request = self.encode({
            'type': 'register',
            'username': parts[0],
            'hash': hash_b64
        })
        self.Core.connector.socket.send(request)

    @check_connection()
    @debug_log # /auth <username> <password>
    def auth(self, text):
        """Запрос на вход в акк"""
        parts = text.split()
        if len(parts) != 2:
            print('Правильное использование: /auth <юзернейм> <пароль>')
            return
        salt = self._get_salt(parts[0])
        if not salt:
            return
        salt_bytes = base64.b64decode(salt.encode('utf-8'))
        hash_pwd = hashlib.pbkdf2_hmac('sha256', parts[1].encode(), salt_bytes, 100000)
        hash_b64 = base64.b64encode(hash_pwd).decode('utf-8')
        request = self.encode({
            'type': 'auth',
            'username': parts[0],
            'hash': hash_b64
        })
        self.Core.connector.socket.send(request)

    @check_connection()
    @debug_log
    def _get_salt(self, username):
        """Запрос соли для регистрации/входа"""
        request = self.encode({
            'type': 'get_salt',
            'username': username
        })
        self.Core.connector.socket.send(request)
        answer = self.Handlers.receiver_handler.wait_for('return_salt')
        if not answer:
            print('Превышено время ожидания сервера')
            return None
        return answer.get('salt')