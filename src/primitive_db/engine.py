import shlex

from .core import (
    create_table,
    delete,
    drop_table,
    format_table_output,
    get_table_columns,
    get_table_info,
    insert,
    list_tables,
    select,
    update,
)
from .parser import parse_set_clause, parse_values, parse_where_clause
from .utils import load_metadata, save_metadata


def print_help():
    """Выводит справку по командам работы с данными."""
    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values "
          "(<значение1>, <значение2>, ...) - создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> "
          "- прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
          "where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> "
          "- удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


def run():
    """
    Главная функция, запускающая основной цикл работы с базой данных.
    """
    print("Добро пожаловать в примитивную базу данных!")
    print_help()

    while True:
        try:
            user_input = input("\n>>>Введите команду: ").strip()
            if not user_input:
                continue

            args = shlex.split(user_input)
            command = args[0].lower()

            metadata = load_metadata()

            if command == 'exit':
                print("Выход из программы.")
                break

            elif command == 'help':
                print_help()

            elif command == 'create_table':
                _handle_create_table(metadata, args)

            elif command == 'drop_table':
                _handle_drop_table(metadata, args)

            elif command == 'list_tables':
                _handle_list_tables(metadata)

            elif command == 'insert':
                _handle_insert(metadata, args)

            elif command == 'select':
                _handle_select(metadata, args)

            elif command == 'update':
                _handle_update(metadata, args)

            elif command == 'delete':
                _handle_delete(metadata, args)

            elif command == 'info':
                _handle_info(metadata, args)

            else:
                print(f'Функции "{command}" нет. Попробуйте снова.')

        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
        except Exception as e:
            # Общая обработка ошибок парсинга
            print(f'Ошибка ввода: {e}')


def _handle_create_table(metadata, args):
    """Обрабатывает команду create_table."""
    if len(args) < 3:
        print("Ошибка: Недостаточно аргументов. Использование: "
              "create_table <имя_таблицы> <столбец1:тип> ...")
        return

    table_name = args[1]
    columns = args[2:]

    result = create_table(metadata, table_name, columns)
    if result:
        save_metadata(result)
        table_columns = get_table_columns(result, table_name)
        print(f'Таблица "{table_name}" успешно создана со столбцами: '
              f'{", ".join(table_columns)}')


def _handle_drop_table(metadata, args):
    """Обрабатывает команду drop_table."""
    if len(args) != 2:
        print("Ошибка: Неверное количество аргументов. "
              "Использование: drop_table <имя_таблицы>")
        return

    table_name = args[1]

    result = drop_table(metadata, table_name)
    if result:
        save_metadata(result)
        print(f'Таблица "{table_name}" успешно удалена.')


def _handle_list_tables(metadata):
    """Обрабатывает команду list_tables."""
    tables = list_tables(metadata)
    if tables is not None:
        if tables:
            print("Список таблиц:")
            for table in tables:
                print(f"- {table}")
        else:
            print("Нет созданных таблиц.")


def _handle_insert(metadata, args):
    """Обрабатывает команду insert."""
    if len(args) < 4 or args[1].lower(
    ) != 'into' or args[3].lower() != 'values':
        print("Ошибка: Неверный формат команды. Использование: "
              "insert into <имя_таблицы> values (<значение1>, <значение2>, ...)")
        return

    table_name = args[2]
    values_str = ' '.join(args[4:])

    try:
        values = parse_values(values_str)
        result = insert(metadata, table_name, values)
        if result:
            table_data, new_id = result
            print(f'Запись с ID={new_id} успешно добавлена '
                  f'в таблицу "{table_name}".')
    except Exception as e:
        print(f'Ошибка парсинга: {e}')


def _handle_select(metadata, args):
    """Обрабатывает команду select."""
    if len(args) < 3 or args[1].lower() != 'from':
        print("Ошибка: Неверный формат команды. Использование: "
              "select from <имя_таблицы> [where <условие>]")
        return

    table_name = args[2]
    where_clause = None

    if len(args) > 4 and args[3].lower() == 'where':
        where_str = ' '.join(args[4:])
        try:
            where_clause = parse_where_clause(where_str)
        except Exception as e:
            print(f'Ошибка в условии WHERE: {e}')
            return

    records = select(table_name, where_clause)
    if records is not None and table_name in metadata:
        table_columns = metadata[table_name]
        formatted_output = format_table_output(records, table_columns)
        print(formatted_output)


def _handle_update(metadata, args):
    """Обрабатывает команду update."""
    if len(args) < 7 or args[2].lower() != 'set' or 'where' not in [
            arg.lower() for arg in args]:
        print("Ошибка: Неверный формат команды. Использование: "
              "update <имя_таблицы> set <столбец>=<значение> where <условие>")
        return

    table_name = args[1]

    set_index = args.index('set') if 'set' in args else -1
    where_index = args.index('where') if 'where' in args else -1

    if set_index == -1 or where_index == -1:
        print("Ошибка: Неверный формат команды. "
              "Должны присутствовать SET и WHERE.")
        return

    set_str = ' '.join(args[set_index + 1:where_index])
    where_str = ' '.join(args[where_index + 1:])

    try:
        set_clause = parse_set_clause(set_str)
        where_clause = parse_where_clause(where_str)

        if not set_clause:
            print("Ошибка: Не указаны значения для обновления.")
            return

        if not where_clause:
            print("Ошибка: Не указано условие WHERE.")
            return

        result = update(table_name, set_clause, where_clause)
        if result:
            table_data, updated_count = result
            print(f'Успешно обновлено {updated_count} записей '
                  f'в таблице "{table_name}".')
    except Exception as e:
        print(f'Ошибка парсинга: {e}')


def _handle_delete(metadata, args):
    """Обрабатывает команду delete."""
    if len(args) < 5 or args[1].lower(
    ) != 'from' or args[3].lower() != 'where':
        print("Ошибка: Неверный формат команды. Использование: "
              "delete from <имя_таблицы> where <условие>")
        return

    table_name = args[2]
    where_str = ' '.join(args[4:])

    try:
        where_clause = parse_where_clause(where_str)
        if not where_clause:
            print("Ошибка: Не указано условие WHERE.")
            return

        result = delete(table_name, where_clause)
        if result:
            table_data, deleted_count = result
            print(f'Успешно удалено {deleted_count} записей '
                  f'из таблицы "{table_name}".')
    except Exception as e:
        print(f'Ошибка парсинга: {e}')


def _handle_info(metadata, args):
    """Обрабатывает команду info."""
    if len(args) != 2:
        print("Ошибка: Неверное количество аргументов. "
              "Использование: info <имя_таблицы>")
        return

    table_name = args[1]

    table_info = get_table_info(metadata, table_name)
    if table_info:
        print(f"Таблица: {table_info['name']}")
        print(f"Столбцы: {', '.join(table_info['columns'])}")
        print(f"Количество записей: {table_info['record_count']}")
