import socket
import threading
import logging
import time

from Server.core.config import setup_logger


setup_logger()

class ClientManager:
    def __init__(self, addr, Handlers):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.addr = addr
        self.Handlers = Handlers

        self.socket = socket.socket()
        self.socket.bind(self.addr)
        self.socket.listen(10)
        self.running = threading.Event(); self.running.set()

        self.clients = {} # {addr: {'registered': False, ...}, ...} все клиенты онлайн

        self.handl_connections_thr = threading.Thread(target=self.handl_connections)
        self.handl_connections_thr.start()
        self.logger.debug('Инициализирован')

    def handl_connections(self):
        """Цикл подключений новых юзеров"""
        while self.running.is_set():
            self.connect_user()
            time.sleep(0.1)

    def connect_user(self):
        try:
            client_socket, client_addr = self.socket.accept()
            client_addr = f'{client_addr[0]}:{client_addr[1]}'
            self.clients[client_addr] = {
                'socket': client_socket,
                'auth': False
            }
            threading.Thread(
                target= self.Handlers.client_handler.receive,
                args=(client_addr,),
                daemon=True
            ).start()
            self.logger.info(f'Подключился клиент: {client_addr}')
        except:
            return

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

    def remove_client(self, client_addr):
        """Безопасно удаляет клиента"""
        if client_addr in self.clients:
            try:
                self.clients[client_addr]['socket'].close()
            except:
                pass
            del self.clients[client_addr]
            self.logger.info(f'Удалили клиента: {client_addr} ')
            return True
        return False

    def _get_addr_by_nickname(self, nickname):
        """Возвращает адрес клиента по никнейму"""
        for addr, client in self.clients.items():
            if client.get('nickname') == nickname:
                return addr