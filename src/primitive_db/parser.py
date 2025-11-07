import shlex


def parse_where_clause(where_string):
    """
    Парсит условие WHERE в формате "столбец = значение".
    
    Args:
        where_string (str): Строка условия
        
    Returns:
        dict: Словарь с условием {столбец: значение}
        
    Raises:
        ValueError: Если формат некорректный
    """
    if not where_string:
        return None
    
    parts = where_string.split('=', 1)
    if len(parts) != 2:
        raise ValueError('Некорректный формат условия WHERE. Используйте: "столбец = значение"')
    
    column = parts[0].strip()
    value = parts[1].strip()
    
    # Убираем кавычки если есть
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    
    return {column: _convert_value(value)}


def parse_set_clause(set_string):
    """
    Парсит условие SET в формате "столбец1 = значение1, столбец2 = значение2".
    
    Args:
        set_string (str): Строка установки значений
        
    Returns:
        dict: Словарь с устанавливаемыми значениями {столбец: значение}
        
    Raises:
        ValueError: Если формат некорректный
    """
    if not set_string:
        return {}
    
    set_dict = {}
    assignments = set_string.split(',')
    
    for assignment in assignments:
        parts = assignment.split('=', 1)
        if len(parts) != 2:
            raise ValueError(f'Некорректный формат присваивания: {assignment}')
        
        column = parts[0].strip()
        value = parts[1].strip()
        
        # Убираем кавычки если есть
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        
        set_dict[column] = _convert_value(value)
    
    return set_dict


def parse_values(values_string):
    """
    Парсит значения в формате "(значение1, значение2, ...)".
    
    Args:
        values_string (str): Строка со значениями
        
    Returns:
        list: Список значений
        
    Raises:
        ValueError: Если формат некорректный
    """
    if not values_string.startswith('(') or not values_string.endswith(')'):
        raise ValueError('Значения должны быть в круглых скобках')
    
    # Убираем скобки
    values_content = values_string[1:-1].strip()
    if not values_content:
        return []
    
    # Используем улучшенный парсинг
    values = _advanced_split_values(values_content)
    
    return [_convert_value(v) for v in values]


def _advanced_split_values(values_string):
    """
    Улучшенный разбор значений, корректно обрабатывающий кавычки и запятые.
    """
    result = []
    current = ''
    in_quotes = False
    quote_char = None
    escape = False
    
    for i, char in enumerate(values_string):
        if escape:
            current += char
            escape = False
        elif char == '\\':
            escape = True
        elif char in ['"', "'"]:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
            current += char
        elif char == ',' and not in_quotes:
            result.append(current.strip())
            current = ''
        else:
            current += char
    
    # Добавляем последнее значение
    if current.strip():
        result.append(current.strip())
    
    return result


def _simple_split_values(values_string):
    """
    Простой разбор значений, учитывающий кавычки.
    """
    result = []
    current = ''
    in_quotes = False
    quote_char = None
    
    for char in values_string:
        if char in ['"', "'"] and not in_quotes:
            in_quotes = True
            quote_char = char
            current += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current += char
        elif char == ',' and not in_quotes:
            result.append(current.strip())
            current = ''
        else:
            current += char
    
    if current.strip():
        result.append(current.strip())
    
    return result


def _convert_value(value_str):
    """
    Конвертирует строковое значение в соответствующий тип.
    
    Args:
        value_str (str): Строковое значение
        
    Returns:
        Преобразованное значение (int, bool, str)
    """
    # Убираем внешние кавычки для проверки типа
    clean_value = value_str.strip()
    if (clean_value.startswith('"') and clean_value.endswith('"')) or (clean_value.startswith("'") and clean_value.endswith("'")):
        return clean_value[1:-1]
    
    # Проверяем булево значение
    if clean_value.lower() == 'true':
        return True
    elif clean_value.lower() == 'false':
        return False
    
    # Проверяем целое число
    try:
        return int(clean_value)
    except ValueError:
        pass
    # Обрабатываем числа с плавающей точкой (если нужно)
    try:
        return float(clean_value)
    except ValueError:
        pass
    # Возвращаем как строку
    return clean_value