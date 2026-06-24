import logging
import sys

from Server.core.config import setup_logger


setup_logger()


class AdminCommands:
    def __init__(self, Managers):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Managers = Managers

    def close_server(self, text):
        if self.Managers.client_manager.running.is_set():
            self.logger.info('Закрытие сервера...')
            print('Закрытие сервера...')
            self.Managers.client_manager._close_socket()
            self.Managers.client_manager.running.clear()
            sys.exit(0)

    def users_dict(self, text):
        if not self.Managers.client_manager.clients.items():
            print('Подключённых пользователей нет')
        for addr, client in self.Managers.client_manager.clients.items():
            username = client.get('username', 'Нет логина')
            nickname = client.get('nickname', 'Нет ника')
            auth = "✅" if client.get('auth') else "❌"
            self.logger.debug(f"{auth} {nickname} (@{username}) — {addr}")
            print(f"{auth} {nickname} (@{username}) — {addr}")

    def help(self, text):
        print("""Доступные команды:
    /users                      - посмотреть словарь с пользователями
    /close_server               - безопасное закрытие сервера
    /help                       - эта справка""")