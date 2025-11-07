from .utils import load_metadata, save_metadata, load_table_data, save_table_data
from prettytable import PrettyTable


def create_table(metadata, table_name, columns):
    """
    Создает новую таблицу в метаданных.
    """
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')
    
    allowed_types = {'int', 'str', 'bool'}
    table_columns = ['ID:int']
    
    for column in columns:
        if ':' not in column:
            raise ValueError(f'Некорректный формат столбца: {column}. Используйте "имя:тип"')
        
        col_name, col_type = column.split(':', 1)
        col_type = col_type.lower()
        
        if col_type not in allowed_types:
            raise ValueError(f'Неподдерживаемый тип данных: {col_type}. Допустимые типы: {", ".join(allowed_types)}')
        
        table_columns.append(f'{col_name}:{col_type}')
    
    metadata[table_name] = table_columns
    return metadata


def drop_table(metadata, table_name):
    """
    Удаляет таблицу из метаданных.
    """
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    
    del metadata[table_name]
    return metadata


def list_tables(metadata):
    """
    Возвращает список всех таблиц.
    """
    return list(metadata.keys())


def get_table_columns(metadata, table_name):
    """
    Возвращает список столбцов таблицы.
    """
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    
    return metadata[table_name]


def get_table_schema(metadata, table_name):
    """
    Возвращает схему таблицы в виде словаря {имя_столбца: тип}.
    """
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    
    schema = {}
    for col_def in metadata[table_name]:
        col_name, col_type = col_def.split(':')
        schema[col_name] = col_type
    return schema


def insert(metadata, table_name, values):
    """
    Вставляет новую запись в таблицу.
    """
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    
    # Загружаем текущие данные
    table_data = load_table_data(table_name)
    
    # Получаем схему таблицы
    schema = get_table_schema(metadata, table_name)
    column_names = list(schema.keys())
    
    # Проверяем количество значений (без ID)
    expected_values_count = len(column_names) - 1
    if len(values) != expected_values_count:
        raise ValueError(f'Ожидается {expected_values_count} значений, получено {len(values)}')
    
    # Генерируем новый ID
    if table_data:
        new_id = max(record.get('ID', 0) for record in table_data) + 1
    else:
        new_id = 1
    
    # Создаем новую запись
    new_record = {'ID': new_id}
    
    # Заполняем значения (пропускаем ID - он уже есть)
    for i, col_name in enumerate(column_names[1:], start=0):
        value = values[i]
        expected_type = schema[col_name]
        
        # Проверяем тип и при необходимости преобразуем
        if expected_type == 'int':
            if not isinstance(value, int):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    raise ValueError(f'Столбец "{col_name}" ожидает тип int, получено {type(value).__name__}')
        elif expected_type == 'bool':
            if not isinstance(value, bool):
                if isinstance(value, str):
                    if value.lower() in ['true', '1', 'yes']:
                        value = True
                    elif value.lower() in ['false', '0', 'no']:
                        value = False
                    else:
                        raise ValueError(f'Столбец "{col_name}" ожидает тип bool, получено {value}')
                else:
                    raise ValueError(f'Столбец "{col_name}" ожидает тип bool, получено {type(value).__name__}')
        elif expected_type == 'str':
            if not isinstance(value, str):
                value = str(value)
        
        new_record[col_name] = value
    
    # Добавляем запись и сохраняем
    table_data.append(new_record)
    save_table_data(table_name, table_data)
    
    return table_data, new_id


def select(table_name, where_clause=None):
    """
    Выбирает записи из таблицы.
    
    Args:
        table_name (str): Имя таблицы
        where_clause (dict): Условие фильтрации
        
    Returns:
        list: Отфильтрованные записи
    """
    table_data = load_table_data(table_name)
    
    if not where_clause:
        return table_data
    
    # Фильтруем записи
    filtered_data = []
    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or record[column] != value:
                match = False
                break
        if match:
            filtered_data.append(record)
    
    return filtered_data


def update(table_name, set_clause, where_clause):
    """
    Обновляет записи в таблице.
    
    Args:
        table_name (str): Имя таблицы
        set_clause (dict): Устанавливаемые значения
        where_clause (dict): Условие фильтрации
        
    Returns:
        tuple: (обновленные данные, количество обновленных записей)
    """
    table_data = load_table_data(table_name)
    updated_count = 0
    
    for record in table_data:
        # Проверяем условие WHERE
        match = True
        for column, value in where_clause.items():
            if column not in record or record[column] != value:
                match = False
                break
        
        if match:
            # Обновляем запись
            for column, new_value in set_clause.items():
                if column in record and column != 'ID':  # ID нельзя менять
                    record[column] = new_value
            updated_count += 1
    
    if updated_count > 0:
        save_table_data(table_name, table_data)
    
    return table_data, updated_count


def delete(table_name, where_clause):
    """
    Удаляет записи из таблицы.
    
    Args:
        table_name (str): Имя таблицы
        where_clause (dict): Условие фильтрации
        
    Returns:
        tuple: (обновленные данные, количество удаленных записей)
    """
    table_data = load_table_data(table_name)
    initial_count = len(table_data)
    
    # Фильтруем записи, которые НЕ соответствуют условию WHERE
    filtered_data = []
    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or record[column] != value:
                match = False
                break
        
        if not match:
            filtered_data.append(record)
    
    deleted_count = initial_count - len(filtered_data)
    
    if deleted_count > 0:
        save_table_data(table_name, filtered_data)
    
    return filtered_data, deleted_count


def format_table_output(records, columns):
    """
    Форматирует записи в виде красивой таблицы.
    
    Args:
        records (list): Список записей
        columns (list): Список столбцов в формате ['name:type', ...]
        
    Returns:
        str: Отформатированная таблица
    """
    if not records:
        return "Нет данных для отображения."
    
    # Создаем таблицу
    table = PrettyTable()
    
    # Получаем имена столбцов
    column_names = [col.split(':')[0] for col in columns]
    table.field_names = column_names
    
    # Добавляем записи
    for record in records:
        row = [record.get(col_name, '') for col_name in column_names]
        table.add_row(row)
    
    return table.get_string()


def get_table_info(metadata, table_name):
    """
    Возвращает информацию о таблице.
    
    Args:
        metadata (dict): Метаданные базы данных
        table_name (str): Имя таблицы
        
    Returns:
        dict: Информация о таблице
    """
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    
    table_data = load_table_data(table_name)
    
    return {
        'name': table_name,
        'columns': metadata[table_name],
        'record_count': len(table_data)
    }