import logging

from Server.core.config import setup_logger
from Server.core.json_protocol import JsonProtocol


setup_logger()


class ClientHandler(JsonProtocol):
    def __init__(self, addr, Protocols, Managers):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.addr = addr
        self.Managers = Managers
        self.Protocols = Protocols

        self.typs = {
            'private_message': self.Protocols.client_messages.private_message,
            'set_nickname': self.Protocols.client_messages.set_nickname,
            'get_users_list': self.Protocols.client_messages.return_users_list,
            'get_salt': self.Managers.auth_manager.return_salt,
            'register': self.Managers.auth_manager.register,
            'auth': self.Managers.auth_manager.auth
        }

        self.logger.debug('Инициализирован')

    def receive(self, client_addr):
        """Приём и обработка сообщений от клиента"""
        while True:
            try:
                raw_data = self.Managers.client_manager.clients[client_addr].get('socket').recv(4096)
                if not raw_data:
                    self.logger.info(f'Отключился клиент: {client_addr}')
                    del self.Managers.client_manager.clients[client_addr]
                    break
                data = self.decode(raw_data)
                data_type = data.get('type')
                if data_type in self.typs.keys():
                    self.typs[data_type](client_addr, data)
                    self.logger.debug(f'{client_addr}: {data}')
                else:
                    self.logger.error(f'Тип {data_type} сообщения от пользователя {client_addr} не поддерживается')
            except Exception as err:
                self.logger.error(f'Неизвестная ошибка: {err}')
                break