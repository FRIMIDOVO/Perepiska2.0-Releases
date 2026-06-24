import logging

from Demos.win32ts_logoff_disconnected import username

from Server.core.config import setup_logger, check_auth
from Server.core.json_protocol import JsonProtocol
from Server.core.respons_protocol import ResponsProtocol


setup_logger()


class ClientMessages(JsonProtocol, ResponsProtocol):
    def __init__(self, Managers):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Managers = Managers
        self.logger.debug('Инициализирован')

    @check_auth
    def private_message(self, client_addr, data):
        """Пересылает получателю приватное сообщение"""
        to_nick = data.get('to')
        data = {
            'type': 'private_message',
            'text': data.get('text'),
            'from': self.Managers.client_manager.clients.get(client_addr).get('nickname'),
            'time': data.get('time')
        }
        self.send_or_queue(client_addr, to_nick, data)

    @check_auth
    def set_nickname(self, client_addr, data):
        """Устанавливает для пользоватяеля никнейм"""
        nickname = data.get('nickname')
        for addr, client in self.Managers.client_manager.clients.items():
            if client.get('nickname') == nickname:
                self._error(client_addr, f'Пользователь с ником {nickname} уже существует')
                return
        self.Managers.client_manager.clients[client_addr]['nickname'] = nickname
        self.Managers.auth_manager.update_nick(client_addr, nickname)
        self._info(client_addr, f'Для вас установлен никнейм {nickname}')
        self.logger.info(f'Для клиента {client_addr} установлен никнейм {nickname}')

    @check_auth
    def return_users_list(self, client_addr, data):
        """Возвращает список всех зарегистрированных пользователей с их статусом"""
        users_list = []
        for username, user in self.Managers.auth_manager.auth_dict.items():
            nickname = user.get('nickname')
            if not nickname:
                continue
            # Проверяем, онлайн ли пользователь
            addr = self.Managers.client_manager._get_addr_by_nickname(nickname)
            online = False
            if addr and addr in self.Managers.client_manager.clients:
                online = self.Managers.client_manager.clients[addr].get('auth', False)
            users_list.append({
                'nickname': nickname,
                'online': online
            })
        raw_data = self.encode({
            'type': 'return_users_list',
            'list': users_list
        })
        self.Managers.client_manager.clients[client_addr]['socket'].send(raw_data)
        self.logger.debug(f'Отправили клиенту {client_addr} список пользователей ({len(users_list)} чел.)')

    @check_auth
    def return_offline_sms(self, client_addr, data):
        client = self.Managers.client_manager.clients[client_addr]
        username = client.get('username')
        client_socket = client.get('socket')
        self.Managers.sms_manager.deliver_all_messages(username, client_socket)

    def send_or_queue(self, client_addr, to_nick, message_data):
        to_username = self.Managers.auth_manager._get_username_by_nickname(to_nick)
        if not to_username:
            self._error(client_addr, f'Пользователь "{to_nick}" не найден')
            return False

        recipient_addr = self.Managers.client_manager._get_addr_by_nickname(to_nick)
        recipient_online = False
        if recipient_addr and recipient_addr in self.Managers.client_manager.clients:
            recipient = self.Managers.client_manager.clients[recipient_addr]
            recipient_online = recipient.get('auth', False)

        if recipient_online:
            self.Managers.client_manager.clients[recipient_addr]['socket'].send(self.encode(message_data))
            self.logger.info(f'Переслали сообщение от {client_addr} --> {recipient_addr}')
            return True
        else:
            self.Managers.sms_manager.add_message(to_username, message_data)
            self._info(client_addr, f'Сообщение сохранено для {to_nick} (офлайн)')
            self.logger.info(f'Сохранили сообщение от {client_addr} --> {recipient_addr}')
            return False