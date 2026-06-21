import threading
import logging
import time

from Client.core.config import setup_logger, check_connection, debug_log
from Client.core.json_protocol import JsonProtocol


setup_logger()


class ReceiverHandler(JsonProtocol):
    def __init__(self, Core, Protocols):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Core = Core; self.addr = self.Core.addr
        self.Protocols = Protocols

        self.typs = {
            'error': self.Protocols.messages.error,
            'private_message': self.Protocols.messages.private_message,
            'info': self.Protocols.messages.info,
            'return_users_list': self.Protocols.messages.return_users_list,
            'return_salt': self.Protocols.messages.return_salt
        }

        self.receive_thr = threading.Thread(target=self.receive_loop, daemon=True)
        self.receive_thr.start()
        self.logger.debug('Инициализирован')

    def receive_loop(self):
        """Цикл чтения сообщений от сервера"""
        while True:
            self.receive()

    @check_connection(silent=True)
    def receive(self):
        raw_data = self.Core.connector.socket.recv(4096)
        if not raw_data:
            pass
        data = self.decode(raw_data)
        data_type = data.get('type')
        self.typs[data_type](data)

    @debug_log
    def wait_for(self, data_type, timeout=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            answer = self.Protocols.messages._get_answer(data_type)
            if answer is not None:
                return answer
            time.sleep(0.1)
        self.logger.info(f'Таймаут ожидания {data_type}')
        return None