import json
import yaml
import os


class ConfigLoader:
    def __init__(self, config_path="questions.json"):
        self.config_path = config_path
        self.questions = []
        self.config = {}
        self.load_config()

    def load_config(self):
        """Загружает конфигурацию из файла"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Конфигурационный файл не найден: {self.config_path}")

        _, ext = os.path.splitext(self.config_path)

        if ext.lower() in ['.yaml', '.yml']:
            self._load_yaml()
        else:
            self._load_json()

        self._validate_config()
        print(f"✅ Загружено {len(self.questions)} вопросов")

    def _load_json(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.questions = data.get('survey_questions', [])
            self.config = data.get('survey_config', {})

    def _load_yaml(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            self.questions = data.get('survey_questions', [])
            self.config = data.get('survey_config', {})

    def _validate_config(self):
        """Проверяет валидность конфигурации"""
        if not isinstance(self.questions, list):
            raise ValueError("survey_questions должен быть списком")

        for i, question in enumerate(self.questions):
            if 'id' not in question:
                raise ValueError(f"Вопрос #{i + 1} не содержит поле 'id'")
            if 'text' not in question:
                raise ValueError(f"Вопрос #{i + 1} не содержит поле 'text'")
            if 'type' not in question:
                raise ValueError(f"Вопрос #{i + 1} не содержит поле 'type'")