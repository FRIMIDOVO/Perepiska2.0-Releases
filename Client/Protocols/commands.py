import logging
import sys
from datetime import datetime

from Client.core.config import setup_logger, check_connection, debug_log
from Client.core.json_protocol import JsonProtocol


setup_logger()


class Commands(JsonProtocol):
    def __init__(self, Core, Protocols):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Core = Core
        self.Protocols = Protocols
        self.logger.debug('Инициализирован')

    def help(self, text):
        help_text = """
    Доступные команды:

      🔐 Авторизация и регистрация
        /reg <юзернейм> <пароль> <пароль>          — зарегистрироваться на сервере
        /auth <юзернейм> <пароль>                  — аутентифицироваться на сервере

      👤 Профиль и общение
        /set_nick <никнейм>                        — установить отображаемый никнейм
        /msg <никнейм> <сообщение>                 — отправить личное сообщение
        /offline_sms                               — получить сообщения, пришедшие в ваше отсутствие
        /get_users                                 — посмотреть список онлайн-пользователей

      📂 Файлы
        /all_files [количество]                    — показать последние файлы (все, если число не указано)
        /send_file <никнейм> <имя_файла> [текст]   — отправить файл из папки data/files
        /load_file <имя_файла>                     — скачать файл, присланный вам

      🛠️ Системные
        /help                                      — показать эту справку
        /exit                                      — выход из программы (рекомендуется)

    """
        print(help_text)

    @check_connection
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

    @check_connection
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

    @check_connection
    @debug_log
    def get_users_list(self):
        """Запрос на список пользователей"""
        raw_data = self.encode({'type': 'get_users_list'})
        self.Core.connector.socket.send(raw_data)

    @check_connection
    @debug_log
    def get_offline_sms(self, text):
        """Запрос на все сообщзения в отстутствие пользователя"""
        raw_data = self.encode({'type': 'get_offline_sms'})
        self.Core.connector.socket.send(raw_data)

    @check_connection
    @debug_log
    def load_file(self, name):
        """Запрос на загрузку файла по имени"""
        file_id = self.Protocols.file_commands.get_id_by_name(name)
        if not file_id:
            return
        msg = self.encode({
            'type': 'load_file',
            'file_id': file_id
        })
        self.Core.connector.socket.send(msg)

    @debug_log # /all_files <количество штук> - выводит последние файлы или по кол-во, введённое в арг
    def all_files(self, text):
        meta = self.load_from_file('data/files_meta.json')
        if not meta:
            print('У вас нет сохранённых файлов')
            return
        parts = text.strip().split()
        limit = int(parts[0]) if parts and parts[0].isdigit() else None
        sorted_items = sorted(
            meta.items(),
            key=lambda x: x[1].get('time', '00:00'),
            reverse=True
        )
        if limit is not None:
            sorted_items = sorted_items[:limit]
        for file_id, info in sorted_items:
            filename = info.get('filename', '???')
            from_user = info.get('from', '???')
            time_str = info.get('time', '??:??')
            text_msg = info.get('text') or ''
            if text_msg:
                print(f'{time_str}|{from_user}: {filename}; {text_msg}')
            else:
                print(f'{time_str}|{from_user}: {filename}')

    def exit(self, text):
        """Выход из проги с закрытием сокета и остановки процессов"""
        if self.Core.connector.running.is_set():
            self.logger.info('Выход из программы...')
            print('Выход из программы...')
            self.Core.connector._close_socket()
            self.Core.connector.running.clear()
            sys.exit(0)