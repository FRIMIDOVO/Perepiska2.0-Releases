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

    @check_connection
    @debug_log # /reg <username> <password> <password>
    def register(self, login, password):
        """Запрос на регистрацию"""
        salt = self._get_salt(login)
        if not salt:
            return
        salt_bytes = base64.b64decode(salt.encode('utf-8'))
        hash_pwd = hashlib.pbkdf2_hmac('sha256',password.encode(), salt_bytes, 100000)
        hash_b64 = base64.b64encode(hash_pwd).decode('utf-8')
        request = self.encode({
            'type': 'register',
            'username': login,
            'hash': hash_b64
        })
        self.Core.connector.socket.send(request)

    @check_connection
    @debug_log # /auth <username> <password>
    def auth(self, login, passw):
        """Запрос на вход в акк"""
        try:
            salt = self._get_salt(login)
            if not salt:
                return
            salt_bytes = base64.b64decode(salt.encode('utf-8'))
            hash_pwd = hashlib.pbkdf2_hmac('sha256', passw.encode(), salt_bytes, 100000)
            hash_b64 = base64.b64encode(hash_pwd).decode('utf-8')
            request = self.encode({
                'type': 'auth',
                'username': login,
                'hash': hash_b64
            })
            self.Core.connector.socket.send(request)
        except Exception as err:
            print(err)

    @check_connection
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