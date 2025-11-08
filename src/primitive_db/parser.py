def parse_where_clause(where_str):
    """
    Парсит строку условия WHERE в словарь.
    """
    conditions = {}
    parts = where_str.split(' and ')
    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Удаляем кавычки если есть
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            elif value.isdigit():
                value = int(value)
            elif value.lower() in ['true', 'false']:
                value = value.lower() == 'true'

            conditions[key] = value
    return conditions


def parse_set_clause(set_str):
    """
    Парсит строку SET в словарь.
    """
    set_clause = {}
    parts = set_str.split(',')
    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Удаляем кавычки если есть
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            elif value.isdigit():
                value = int(value)
            elif value.lower() in ['true', 'false']:
                value = value.lower() == 'true'

            set_clause[key] = value
    return set_clause


def parse_values(values_str):
    """
    Парсит строку значений VALUES в список значений.
    """
    values = []
    # Удаляем скобки если есть
    if values_str.startswith('(') and values_str.endswith(')'):
        values_str = values_str[1:-1]

    parts = values_str.split(',')
    for part in parts:
        value = part.strip()

        # Удаляем кавычки если есть
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        elif value.isdigit():
            value = int(value)
        elif value.lower() in ['true', 'false']:
            value = value.lower() == 'true'

        values.append(value)
    return values
