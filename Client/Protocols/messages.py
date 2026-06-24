import logging

from Client.core.config import setup_logger


setup_logger()


class Messages:
    def __init__(self, Protocols):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Protocols = Protocols

        self.responses = []
        self.logger.debug('Инициализирован')

    def _get_answer(self, data_type):
        for i, resp in enumerate(self.responses):
            if resp.get('type') == data_type:
                return self.responses.pop(i)
        return None

    def error(self, data):
        print(f'Ошибка: {data.get("text")}')

    def private_message(self, data):
        print(f'{data.get("time")}|{data.get("from")}: {data.get("text")}')

    def info(self, data):
        print(f'Инфо: {data.get("text")}')

    def return_users_list(self, data):
        users = data.get('list')
        print('Список пользователей:')
        for user in users:
            nickname = user.get('nickname')
            online = user.get('online', False)
            status = '🟢' if online else '🔴'
            print(f'{status} {nickname}')

    def file(self, data):
        print(f'{data.get("time")}|{data.get("from")}: {data.get("file_name")}; {data.get("text") or ""}')
        self.Protocols.file_commands.save(data)

    def start_send_file(self, data):
        self.Protocols.file_upload(data)

    def return_salt(self, data):
        self.responses.append(data)