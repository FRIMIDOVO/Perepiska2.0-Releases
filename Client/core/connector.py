import socket
import threading
import logging
import time
from Client.core.config import setup_logger


setup_logger()


class Connector:
    def __init__(self, Core):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.addr = Core.addr
        self.socket = None
        self.disconnect = threading.Event(); self.disconnect.set()
        self.running = threading.Event(); self.running.set()
        self.connection_loop_thr = threading.Thread(target=self.connection_loop)
        self.connection_loop_thr.start()
        self.logger.debug('Инициализирован')

    def connection_loop(self):
        """Цикл, контролирующий подключение к серверу"""
        while self.running.is_set():
            if self.disconnect.is_set():
                self.logger.info('Пытаемся подключится к серверу')
                print('Пытаемся подключится к серверу')
                while not self.connect() and self.running.is_set():
                    time.sleep(3)
                if self.running.is_set():
                    self.disconnect.clear()
            if self.socket and not self.disconnect.is_set():
                try:
                    self.socket.getpeername()
                except:
                    self.logger.warning("Соединение потеряно")
                    self._close_socket()
                    self.disconnect.set()
            time.sleep(3)

    def connect(self):
        """Попытка подключения к серверу"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(self.addr)
            self.logger.info('Успешно подключились!')
            print('Успешно подключились!')
            return True
        except:
            return False

    def _close_socket(self):
        """Безопасное закрытие сокета"""
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.socket.close()
                self.socket = None
                self.logger.info('Сокет закрыт')
            except:
                pass