import logging


def setup_logger(logs_in_file=False, level=logging.DEBUG, log_file='data/logs.log'):
    """Удобные настройки логгера"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        filename=log_file if logs_in_file else None,
        filemode='a' if logs_in_file else None,
        encoding='utf-8' if logs_in_file else None
    )


def check_auth(func):
    """Проверяет авторизацию пользователя на сервере"""
    def wrapper(self, client_addr, data):
        if self.Managers.client_manager.clients.get(client_addr).get('auth'):
            return func(self, client_addr, data)
        else:
            self._error(client_addr, 'Вы не авторизованны на сервере')
    return wrapper


def debug_log(func):
    """Логирует вызов функции на уровне debug"""
    def wrapper(self, *args, **kwargs):
        args_str = ', '.join([str(a) for a in args[1:]])
        self.logger.debug(f'Call: {func.__name__}({args_str})')
        return func(self, *args, **kwargs)
    return wrapper