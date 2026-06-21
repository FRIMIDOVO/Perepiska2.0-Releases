import logging
import secrets
import base64

from Server.core.config import setup_logger
from Server.core.json_protocol import JsonProtocol
from Server.core.respons_protocol import ResponsProtocol


setup_logger()


class AuthManager(JsonProtocol, ResponsProtocol):
    def __init__(self, Managers):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Managers = Managers

        self.path = 'data/users.json'
        self.auth_dict = {}
        self.auth_dict.update(self.load_from_file(self.path))

        self.logger.debug('Инициализирован')

    def return_salt(self, client_addr, data):
        """Возвращает пользователю соль для хэширования"""
        username = data.get('username')
        if username in self.auth_dict.keys():
            salt_b64 = self.auth_dict.get(username).get('salt')
        else:
            salt = secrets.token_bytes(16)
            salt_b64 = base64.b64encode(salt).decode('utf-8')
            self.auth_dict[username] = {
                'salt': salt_b64,
                'hash': ''
            }
        response = self.encode({
            'type': 'return_salt',
            'salt': salt_b64
        })
        self.Managers.client_manager.clients.get(client_addr).get('socket').send(response)
        self.logger.debug(f'Вернули соль клиенту {client_addr}')

    def register(self, client_addr, data):
        """Регистрирует пользователя"""
        username = data.get('username')
        if self.Managers.client_manager.clients.get(client_addr).get('auth'):
            self._error(client_addr, 'Вы уже зарегестрированны и аутентифицированы')
            return
        user = self.auth_dict.get(username)
        if user and user.get('hash'):
            self._error(client_addr, f'Пользователь с ником {username} уже существует')
            return
        self.auth_dict[username].update({
            'hash': data.get('hash'),
            'nickname': username,
            'addr': client_addr
        })
        self.Managers.client_manager.clients[client_addr].update({
            'auth': True,
            'nickname': username,
            'username': username
        })
        self.save_to_file(self.path, self.auth_dict)
        self._info(client_addr, f"""Теперь вы зарегестрированны с юзернеймом "{username}" и его нельзя имзенить.
Вы можете изменить свой никнейм с помощью соответствующей команды, сейчас он совпадает с юзернеймом.""")

    def auth(self, client_addr, data):
        """Аутентифицирует пользователя"""
        username = data.get('username')
        if self.Managers.client_manager.clients.get(client_addr).get('auth'):
            self._error(client_addr, 'Вы уже аутентифицированы')
            return
        if not self.auth_dict.get(username):
            self._error(client_addr, 'Неверный логин или пароль')
            return
        hash = self.auth_dict.get(username).get('hash')
        if not hash:
            self._error(client_addr, 'Неверный логин или пароль')
            return
        if data.get('hash') == hash:
            self.Managers.client_manager.clients[client_addr].update({
                'auth': True,
                'nickname': self.auth_dict[username].get('nickname', username),
                'username': username
            })
            self.auth_dict[username]['addr'] = client_addr
            self._info(client_addr, 'Вы аутентифицированны!')
        else:
            self._error(client_addr, 'Неверный логин или пароль.')

    def _get_username_by_addr(self, addr):
        for us, data in self.auth_dict.items():
            if addr == data.get('addr'):
                return us

    def update_nick(self, addr, nickname):
        username = self._get_username_by_addr(addr)
        if username in self.auth_dict:
            self.auth_dict[username].update({
                'nicname': nickname
            })
            self.save_to_file(self.path, self.auth_dict)