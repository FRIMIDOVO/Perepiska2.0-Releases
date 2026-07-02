import logging

from Client.GUI.toast import Toast


def setup_logger(logs_in_file=False, level=logging.DEBUG, log_file='data/logs.log'):
    """Удобные настройки логгера"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        filename=log_file if logs_in_file else None,
        filemode='a' if logs_in_file else None,
        encoding='utf-8' if logs_in_file else None
    )


def check_connection(func):
    """Декоратор, проверяющий подключение к серверу"""
    def wrapper(self, *args, **kwargs):
        if self.Core.connector.disconnect.is_set():
            self.Core.connector.connection_lost.emit('Нет подключения к серверу')
            return None
        try:
            return func(self, *args, **kwargs)
        except Exception as err:
            self.Core.connector.disconnect.set()
            self.Core.connector.connection_lost.emit(f'{func.__name__}: {err}')
            return None
    return wrapper


def debug_log(func):
    """Логирует вызов функции на уровне дебаг"""
    def wrapper(self, *args, **kwargs):
        self.logger.debug(f'Call: {func.__name__}({",".join([arg for arg in args])})')
        return func(self, *args, **kwargs)
    return wrapper