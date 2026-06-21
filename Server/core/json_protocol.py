import json
import os


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
        """Декодирует дату из JSON"""
        try:
            data = json.loads(raw_data.decode('utf-8'))
            return data
        except json.JSONDecodeError:
            return
        except Exception as e:
            self.logger.error(f'Ошибка при декодировании JSON: {e}')
            return None

    def save_to_file(self, path, data):
        """Сохраняет данные в JSON файл"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.debug(f'Сохранено в {path}')
            return True
        except Exception as e:
            self.logger.error(f'Ошибка сохранения {path}: {e}')
            return False

    def load_from_file(self, path):
        """Загружает данные из JSON файла"""
        if not os.path.exists(path):
            self.logger.debug(f'Файл {path} не найден')
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f'Ошибка загрузки {path}: {e}')
            return {}
