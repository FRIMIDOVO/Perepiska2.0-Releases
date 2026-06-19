import threading
import logging
import time
from Client.core.config import setup_logger, check_connection, debug_log
from Client.core.json_commands import JsonCommands


setup_logger()


class ReceiverHandler(JsonCommands):
    def __init__(self, Core, Handlers):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Core = Core
        self.Handlers = Handlers
        self.addr = self.Core.addr

        self.typs = {
            'error': self.Handlers.messages.error,
            'private_message': self.Handlers.messages.private_message,
            'info': self.Handlers.messages.info,
            'return_users_list': self.Handlers.messages.return_users_list,
            'return_salt': self.Handlers.messages.return_salt
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
            answer = self.Handlers.messages._get_answer(data_type)
            if answer is not None:
                return answer
            time.sleep(0.1)
        self.logger.info(f'Таймаут ожидания {data_type}')
        return None