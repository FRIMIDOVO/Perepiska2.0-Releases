import logging
import time

from Client.core.config import setup_logger

from PyQt5.QtCore import QObject, pyqtSignal


setup_logger()


class Messages(QObject):
    error_msg = pyqtSignal(str)
    info_msg = pyqtSignal(str)

    def __init__(self, Protocols):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Protocols = Protocols

        self.responses = []
        self.logger.debug('Инициализирован')

    def _get_answer(self, data_type, timeout=3):
        start_time = time.time()
        while time.time() - start_time < timeout:
            for i, resp in enumerate(self.responses):
                if resp.get('type') == data_type:
                    return self.responses.pop(i)
        return None

    def error(self, data):
        self.error_msg.emit(data.get('text'))

    def private_message(self, data):
        text = data.get('text')
        fr = data.get('from')
        time = data.get('time')
        print(f'{data.get("time")}|{fr}: {text}')
        # + сохранение в локальную базу данных с сообщениями
        msg_to_save = {
            'sender': fr,
            'text': text,
            'time': time
        }
        self.Protocols.msg_history_db.insert("messages", msg_to_save)

    def info(self, data):
        self.info_msg.emit(data.get('text'))

    def return_users_list(self, data):
        self.responses.append(data)

    def file(self, data):
        print(f'{data.get("time")}|{data.get("from")}: {data.get("file_name")}; {data.get("text") or ""}')
        self.Protocols.file_commands.save(data)

    def start_send_file(self, data):
        self.Protocols.file_upload(data)

    def return_salt(self, data):
        self.responses.append(data)