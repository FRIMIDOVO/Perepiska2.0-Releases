import logging

from Server.core.config import setup_logger, check_auth
from Server.core.json_protocol import JsonProtocol
from Server.core.respons_protocol import ResponsProtocol


setup_logger()


class ClientMessages(JsonProtocol, ResponsProtocol):
    def __init__(self, Managers):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Managers = Managers
        self.logger.debug('Инициализирован')

    def _get_addr_by_nickname(self, nickname):
        """Возвращает адрес клиента по никнейму"""
        for addr, client in self.Managers.client_manager.clients.items():
            if client.get('nickname') == nickname:
                return addr

    @check_auth
    def private_message(self, client_addr, data):
        """Пересылает получателю приватное сообщение"""
        recipient_addr = self._get_addr_by_nickname(data.get('to'))
        if not recipient_addr:
            self._info(client_addr, f'Пользователя с ником {data.get("to")} не существует')
            return
        raw_data = self.encode({
            'type': 'private_message',
            'text': data.get('text'),
            'from': self.Managers.client_manager.clients.get(client_addr).get('nickname'),
            'time': data.get('time')
        })
        self.Managers.client_manager.clients.get(recipient_addr).get('socket').send(raw_data)
        self.logger.debug(f'Переслали сообщение от {client_addr} --> {recipient_addr}')

    @check_auth
    def set_nickname(self, client_addr, data):
        """Устанавливает для пользоватяеля никнейм"""
        nickname = data.get('nickname')
        for addr, client in self.Managers.client_manager.clients.items():
            if client.get('nickname') == nickname:
                self._error(client_addr, f'Пользователь с ником {nickname} уже существует')
                return
        self.Managers.client_manager.clients[client_addr]['nickname'] = nickname
        self.Managers.auth_messages.update_nick(client_addr, nickname)
        self._info(client_addr, f'Для вас установлен никнейм {nickname}')
        self.logger.info(f'Для клиента {client_addr} установлен никнейм {nickname}')

    @check_auth
    def return_users_list(self, client_addr, data):
        """Возвращает пользователю список пользователей"""
        users_list = [client.get('nickname') for addr, client in self.Managers.client_manager.clients.items()]
        raw_data = self.encode({
            'type': 'return_users_list',
            'list': users_list
        })
        self.Managers.client_manager.clients.get(client_addr).get('socket').send(raw_data)
        self.logger.debug(f'Отправили клиенту {client_addr} список пользователей')