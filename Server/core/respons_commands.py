

class ResponsCommands:
    def _error(self, client_addr, text):
        """Отправка пользователю ошибки"""
        raw = self.encode({
            'type': 'error',
            'text': text
        })
        self.Managers.client_manager.clients.get(client_addr).get('socket').send(raw)
        self.logger.debug(f'Вернули ошибку клиенту {client_addr}')

    def _info(self, client_addr, text):
        """Отправка пользователю информации"""
        raw = self.encode({
            'type': 'info',
            'text': text
        })
        self.Managers.client_manager.clients.get(client_addr).get('socket').send(raw)
        self.logger.debug(f'Вернули информацию клиенту {client_addr}')
