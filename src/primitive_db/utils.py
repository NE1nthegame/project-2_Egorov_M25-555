import json
import os
from pathlib import Path


def load_metadata(filepath='db_meta.json'):
    """
    Загружаем метаданные из JSON-файла.

    Args:
        filepath (str): Путь к файлу метаданных

    Returns:
        dict: Словарь с метаданными или пустой словарь если файл не найден
    """
    try:
        with open (filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_metadata(data, filepath='db_meta.json'):
    """
    Сохраняет метаданные в JSON-файл.

    Args:
        data (dict): Данные для сохранения
        filepath (str): Путь к файлу метаданных
    """
    # Создаём директорию если не существует
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)


    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_table_data(table_name, data_dir='data'):
    """
    Загружаем данные таблицы из JSON-файла.

    Args:
        table_name (str): Имя таблицы
        data_dir (str): Директория с данными
    
    Returns:
        list: Cписок записей таблицы
    """

    filepath = Path(data_dir) / f"{table_name}.json"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
def save_table_data(table_name, data, data_dir='data'):
    """
    Сохраняет данные таблицы в JSON-файл.
    
    Args:
        table_name (str): Имя таблицы
        data (list): Данные для сохранения
        data_dir (str): Директория для сохранения
    """
    # Создаем директорию если не существует
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    
    filepath = Path(data_dir) / f"{table_name}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def ensure_data_dir(data_dir='data'):
    """
    Создает директорию для данных если она не существует.
    """
    Path(data_dir).mkdir(parents=True, exist_ok=True)