import logging
import os
from datetime import datetime

from Client.core.config import setup_logger, check_connection, debug_log
from Client.core.json_protocol import JsonProtocol


setup_logger()


class FileCommands(JsonProtocol):
    def __init__(self, Core):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Core = Core

        self.files_path = 'data/files'
        self.meta_path = 'data/files_meta.json'

        self.meta = self.load_from_file(self.meta_path) or {}

        self.logger.debug('Инициализирован')

    @check_connection
    @debug_log # /send_file <никнейм получателя> <имя файла> (должен быть в папке data/files) <текстовое сообщение>
    def send_file(self, text):
        """Фулл функция отправки файла на сервер с предупреждением"""
        parts = text.split(maxsplit=2)
        if len(parts) < 2:
            print('Правильное использование: /send_file <никнейм получателя> <имя файла> (должен быть в папке data/files) <текстовое сообщение>')
            return
        filename = parts[1]
        file_path = os.path.join(self.files_path, filename)
        if not os.path.exists(file_path):
            print(f'Нет файла "{filename}" в папке "data/files"')
            return
        filesize = os.path.getsize(file_path)
        to = parts[0]
        text = parts[2] if len(parts) == 3 else None
        msg = self.encode({
            'type': 'send_file',
            'filename': filename,
            'filesize': filesize,
            'text': text,
            'to': to,
            'time': datetime.now().strftime("%H:%M")
        })
        self.Core.connector.socket.send(msg)
        self._send_chunks(file_path, filename, filesize)

    def _send_chunks(self, file_path, filename, filesize):
        """Почанковая отправка файла на сервер"""
        self.logger.info(f'Отправка файла {filename} ({filesize} байт)')
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    self.Core.connector.socket.send(chunk)
            return True
        except FileNotFoundError:
            self.logger.error(f'Файл {file_path} не найден')
            print(f'Ошибка: файл {file_path} не найден')
            return False
        except Exception as e:
            self.logger.error(f'Ошибка отправки файла: {e}')
            print(f'Ошибка отправки: {e}')
            return False

    @check_connection
    def file_upload(self, data):
        """Функция загрузки файла с сервера"""
        filename = data.get('filename')
        filesize = data.get('filesize')
        text = data.get('text')
        from_nick = data.get('from')
        file_id = data.get('file_id')
        file_path = os.path.join(self.files_path, file_id)
        self.meta[file_id] = {
            'filename': filename,
            'filesize': filesize,
            'text': text,
            'from': from_nick,
            'time': data.get('time'),
            'downloaded': False
        }
        self.save_to_file(self.meta_path, self.meta)
        self._load_chunks(file_id, file_path)

    def _load_chunks(self, file_id, file_path):
        """Почанковая загрузка файла с сервера"""
        meta = self.meta.get(file_id)
        filesize = meta.get('filesize')
        filename = meta.get('filename')
        received = 0
        self.logger.debug(f'Загрузка {meta["filename"]} ({filesize} байт)')
        print(f'Загрузка {meta["filename"]} ({filesize} байт)')
        try:
            with open(file_path, 'wb') as f:
                while received < filesize:
                    chunk = self.Core.connector.socket.recv(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
            print(f'Файл {filename} загружен!')
            self.meta[file_id]['downloaded'] = True
            self.save_to_file(self.meta_path, self.meta)
            return True
        except Exception as e:
            self.logger.error(f'Ошибка загрузки файла: {e}')
            print(f'Ошибка загрузки: {e}')
            return False

    def get_id_by_name(self, filename):
        """Возвращает file_id по имени файла из локальной меты"""
        ids = []
        for file_id, meta in self.meta.items():
            if meta.get('filename') == filename:
                ids.append(file_id)
        if not ids:
            print(f'Файла с именем {filename} нет в вашем доступе или неверное имя файла')
            return
        return sorted(ids)[-1]

    def save(self, data):
        """Сохранение даты в файл с метой"""
        file_id = data.get('file_id')
        filename = data.get('file_name')
        from_nick = data.get('from')
        text = data.get('text', '')
        time = data.get('time')
        filesize = data.get('filesize')
        self.meta[file_id] = {
            'filename': filename,
            'filesize': filesize,
            'text': text,
            'from': from_nick,
            'time': time,
            'downloaded': False
        }
        self.save_to_file(self.meta_path, self.meta)