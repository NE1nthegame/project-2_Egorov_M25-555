import json


def load_metadata():
    """
    Загружает метаданные базы данных из файла.
    """
    try:
        with open('metadata.json', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(metadata):
    """
    Сохраняет метаданные базы данных в файл.
    """
    with open('metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def load_table_data(table_name):
    """
    Загружает данные таблицы из файла.
    """
    filename = f"{table_name}.json"
    try:
        with open(filename, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """
    Сохраняет данные таблицы в файл.
    """
    filename = f"{table_name}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
