import logging
import os
import time

from Server.core.config import setup_logger, check_auth
from Server.core.json_protocol import JsonProtocol
from Server.core.respons_protocol import ResponsProtocol


setup_logger()


class FileMessages(JsonProtocol, ResponsProtocol):
    def __init__(self, Managers, Protocols):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Managers = Managers
        self.Protocols = Protocols

        self.files_path = 'data/files'
        self.meta_path = 'data/files_meta.json'

        self.meta = self.load_from_file(self.meta_path) or {}

        self.logger.debug('Инициализирован')

    @check_auth
    def file_upload(self, client_addr, data):
        print(data)
        filename = data.get('filename')
        filesize = data.get('filesize')
        text = data.get('text')
        from_nick = self.Managers.client_manager.clients.get(client_addr).get('nickname')
        to_nick = data.get('to')
        to_username = self._get_username_by_nickname(to_nick)
        file_id = f"{int(time.time())}_{filename}"
        file_path = os.path.join(self.files_path, file_id)
        self.meta[file_id] = {
            'filename': filename,
            'filesize': filesize,
            'text': text,
            'from': from_nick,
            'to': to_username,
            'time': data.get('time'),
            'uploaded': False
        }
        self.save_to_file(self.meta_path, self.meta)
        self._load_chunks(client_addr, file_id, file_path)
        self._notify_receiver(client_addr, file_id, to_nick)

    def _notify_receiver(self, client_addr, file_id, to_nick):
        """Уведомляет получателя о новом файле"""
        meta = self.meta.get(file_id)
        from_nick = meta.get('from')
        filename = meta.get('filename')
        filesize = meta.get('filesize')
        text = meta.get('text', '')
        time = meta.get('time')
        notification = {
            'type': 'file',
            'file_id': file_id,
            'file_name': filename,
            'filesize': filesize,
            'text': text,
            'from': from_nick,
            'time': time
        }
        self.Protocols.client_messages.send_or_queue(
            client_addr,
            to_nick,
            notification
        )

    def _load_chunks(self, client_addr, file_id, file_path):
        """Почанковая загрузка файла от клиента"""
        meta = self.meta.get(file_id)
        client_socket = self.Managers.client_manager.clients.get(client_addr).get('socket')
        filesize = meta['filesize']
        received = 0
        self.logger.debug(f'Загрузка {meta["filename"]} ({filesize} байт)')
        try:
            with open(file_path, 'wb') as f:
                while received < filesize:
                    chunk = client_socket.recv(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
            if received < filesize:
                self.logger.error(f'Файл {meta["filename"]} загружен не полностью: {received}/{filesize}')
                self._error(client_addr, f'Файл загружен не полностью: {received}/{filesize}')
                return False
            self.meta.get(file_id)['uploaded'] = True
            self.save_to_file(self.meta_path, self.meta)
            self._info(client_addr, f'Файл {meta["filename"]} успешно загружен!')
            self.logger.info(f'Файл {meta["filename"]} загружен')
            return True
        except Exception as e:
            self.logger.error(f'Ошибка загрузки: {e}')
            self._error(client_addr, f'Ошибка загрузки: {e}')
            return False

    @check_auth
    def send_file(self, client_addr, data):
        file_id = data.get('file_id')
        meta = self.meta.get(file_id)
        if not meta:
            self._error(client_addr, f'Файл не найден')
        # Проверяем, что клиент имеет право скачивать этот файл
        client = self.Managers.client_manager.clients.get(client_addr, {})
        client_username = client.get('username')
        to_username = meta.get('to')
        if client_username != to_username:
            self._error(client_addr, 'У вас нет прав на этот файл')
            return
        file_path = os.path.join(self.files_path, file_id)
        if not os.path.exists(file_path):
            self._error(client_addr, 'Файл не найден на сервере')
            return
        filename = meta.get('filename')
        filesize = meta.get('filesize')
        header = self.encode({
            'type': 'start_file_upload',
            'filename': filename,
            'filesize': filesize,
            'file_id': file_id
        })
        self.Managers.client_manager.clients[client_addr]['socket'].send(header)
        self._send_chunks(client_addr, filename, file_path)

    def _send_chunks(self, client_addr, filename, file_path):
        client_socket = self.Managers.client_manager.clients.get(client_addr, {}).get('socket')
        if not client_socket:
            self.logger.error(f'Сокет для {client_addr} не найден')
            return False
        self.logger.info(f'Отправка файла {filename} клиенту {client_addr}')
        try:
            with open(file_path, 'rb') as f:
                sent = 0
                while chunk := f.read(8192):
                    client_socket.send(chunk)
                    sent += len(chunk)
            self.logger.info(f'Файл {filename} отправлен клиенту {client_addr}')
            return True
        except Exception as e:
            self.logger.error(f'Ошибка отправки файла: {e}')
            return False

    def _get_username_by_nickname(self, nickname):
        """Возвращает username по никнейму"""
        for username, user_data in self.Managers.auth_manager.auth_dict.items():
            if user_data.get('nickname') == nickname:
                return username
        return None