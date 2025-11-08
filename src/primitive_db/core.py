from prettytable import PrettyTable

from .decorators import confirm_action, create_cacher, handle_db_errors, log_time
from .utils import load_table_data, save_table_data

# Создаем кэшер для результатов запросов
query_cacher = create_cacher()


@handle_db_errors
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
            raise ValueError(
                f'Некорректный формат столбца: {column}. '
                'Используйте "имя:тип"'
            )

        col_name, col_type = column.split(':', 1)
        col_type = col_type.lower()

        if col_type not in allowed_types:
            raise ValueError(
                f'Неподдерживаемый тип данных: {col_type}. '
                f'Допустимые типы: {", ".join(allowed_types)}'
            )

        table_columns.append(f'{col_name}:{col_type}')

    metadata[table_name] = table_columns
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """
    Удаляет таблицу из метаданных.
    """
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    return metadata


@handle_db_errors
def list_tables(metadata):
    """
    Возвращает список всех таблиц.
    """
    return list(metadata.keys())


@handle_db_errors
def get_table_columns(metadata, table_name):
    """
    Возвращает список столбцов таблицы.
    """
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    return metadata[table_name]


@handle_db_errors
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


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """
    Вставляет новую запись в таблицу.
    """
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    table_data = load_table_data(table_name)
    schema = get_table_schema(metadata, table_name)
    column_names = list(schema.keys())

    expected_values_count = len(column_names) - 1
    if len(values) != expected_values_count:
        raise ValueError(
            f'Ожидается {expected_values_count} значений, '
            f'получено {len(values)}'
        )

    if table_data:
        new_id = max(record['ID'] for record in table_data) + 1
    else:
        new_id = 1

    new_record = {'ID': new_id}

    for i, col_name in enumerate(column_names[1:], start=0):
        value = values[i]
        expected_type = schema[col_name]

        if expected_type == 'int' and not isinstance(value, int):
            raise ValueError(
                f'Столбец "{col_name}" ожидает тип int, '
                f'получено {type(value).__name__}'
            )
        elif expected_type == 'bool' and not isinstance(value, bool):
            raise ValueError(
                f'Столбец "{col_name}" ожидает тип bool, '
                f'получено {type(value).__name__}'
            )
        elif expected_type == 'str' and not isinstance(value, str):
            raise ValueError(
                f'Столбец "{col_name}" ожидает тип str, '
                f'получено {type(value).__name__}'
            )

        new_record[col_name] = value

    table_data.append(new_record)
    save_table_data(table_name, table_data)

    return table_data, new_id


@handle_db_errors
@log_time
def select(table_name, where_clause=None):
    """
    Выбирает записи из таблицы.
    """
    # Создаем ключ для кэша на основе таблицы и условия
    cache_key = f"select_{table_name}_{str(where_clause)}"

    def get_table_data():
        table_data = load_table_data(table_name)

        if not where_clause:
            return table_data

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

    # Используем кэшер для получения данных
    return query_cacher(cache_key, get_table_data)


@handle_db_errors
def update(table_name, set_clause, where_clause):
    """
    Обновляет записи в таблице.
    """
    table_data = load_table_data(table_name)
    updated_count = 0

    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or record[column] != value:
                match = False
                break

        if match:
            for column, new_value in set_clause.items():
                if column in record and column != 'ID':
                    record[column] = new_value
            updated_count += 1

    if updated_count > 0:
        save_table_data(table_name, table_data)

    return table_data, updated_count


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_name, where_clause):
    """
    Удаляет записи из таблицы.
    """
    table_data = load_table_data(table_name)
    initial_count = len(table_data)

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


@handle_db_errors
def format_table_output(records, columns):
    """
    Форматирует записи в виде красивой таблицы.
    """
    if not records:
        return "Нет данных для отображения."

    table = PrettyTable()
    column_names = [col.split(':')[0] for col in columns]
    table.field_names = column_names

    for record in records:
        row = [record.get(col_name, '') for col_name in column_names]
        table.add_row(row)

    return table.get_string()


@handle_db_errors
def get_table_info(metadata, table_name):
    """
    Возвращает информацию о таблице.
    """
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    table_data = load_table_data(table_name)

    return {
        'name': table_name,
        'columns': metadata[table_name],
        'record_count': len(table_data)
    }
