import logging
import sys
from datetime import datetime

from Client.core.config import setup_logger, check_connection, debug_log
from Client.core.json_protocol import JsonProtocol


setup_logger()


class Commands(JsonProtocol):
    def __init__(self, Core):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Core = Core
        self.logger.debug('Инициализирован')

    def help(self, text):
        print(f"""Доступные команды:
    /reg <юзернейм> <пароль> <пароль>          — зарегистрироваться на сервере
    /auth <юзернейм> <пароль>                  — аутентифицироваться на сервере
    /set_nick <никнейм>                        — установить никнейм на сервере
    /msg <никнейм получателя> <сообщение>      — отправить личное сообщение
    /get_users                                 — получить список пользователей
    /help                                      — эта справка
    /exit                                      — выход из программы (рекомендуется)""")

    @check_connection()
    @debug_log
    def private_message(self, text):
        """Отправляет личные сообщения"""
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            print("Правильное использование: /msg <никнейм получателя> <сообщение>")
            return
        raw_data = self.encode({
            'type': 'private_message',
            'text': parts[1],
            'to': parts[0],
            'time': datetime.now().strftime("%H:%M")
        })
        self.Core.connector.socket.send(raw_data)

    @check_connection()
    @debug_log
    def set_nickname(self, nick):
        """Устанавливает никнейм на сервере"""
        if not nick:
            print("Правильное использование: /set_nick <никнейм>")
            return
        raw_data = self.encode({
            'type': 'set_nickname',
            'nickname': nick
        })
        self.Core.connector.socket.send(raw_data)

    @check_connection()
    @debug_log
    def get_users_list(self, text):
        """Запрос серверу на список пользователей"""
        raw_data = self.encode({'type': 'get_users_list'})
        self.Core.connector.socket.send(raw_data)

    def exit(self, text):
        """Выход из проги с закрытием сокета и остановки процессов"""
        self.logger.info('Выход из программы...')
        print('Выход из программы...')
        self.Core.connector._close_socket()
        self.Core.connector.running.clear()
        sys.exit(0)