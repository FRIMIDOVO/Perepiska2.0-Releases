import json


class JsonProtocol:
    def encode(self, data):
        """Кодирует дату в json"""
        try:
            message = json.dumps(data, ensure_ascii=False)
            return message.encode('utf-8')
        except Exception as err:
            self.logger.error(f'Ошибка кодирования в JSON: {err}')
            return None

    def decode(self, raw_data):
        """Декодирует дату из json"""
        try:
            data = json.loads(raw_data.decode('utf-8'))
            return data
        except json.JSONDecodeError as e:
            self.logger.error(f'Ошибка декодирования JSON: {e}')
            return None
        except Exception as e:
            self.logger.error(f'Ошибка при декодировании JSON: {e}')
            return None