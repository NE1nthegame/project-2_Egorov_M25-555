import functools
import time
from typing import Any, Callable


def handle_db_errors(func: Callable) -> Callable:
    """
    Декоратор для обработки ошибок базы данных.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден.")
            return None
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
            return None
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return None
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            return None
    return wrapper


def confirm_action(action_name: str) -> Callable:
    """
    Декоратор для подтверждения опасных операций.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            prompt = (
                f"Вы уверены, что хотите выполнить \"{action_name}\"? "
                f"[y/n]: "
            )
            user_input = input(prompt).strip().lower()
            if user_input in ['y', 'yes', 'да', 'д']:
                return func(*args, **kwargs)
            else:
                print("Операция отменена пользователем.")
                return None
        return wrapper
    return decorator


def log_time(func: Callable) -> Callable:
    """
    Декоратор для измерения времени выполнения функции.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за "
              f"{execution_time:.3f} секунд")
        return result
    return wrapper


def create_cacher():
    """
    Фабрика для создания кэшера с замыканием.
    """
    cache = {}

    def cache_result(key: str, value_func: Callable) -> Any:
        """
        Кэширует результат выполнения функции.
        """
        if key in cache:
            print(f"Используется кэшированный результат для ключа: {key}")
            return cache[key]
        else:
            result = value_func()
            cache[key] = result
            print(f"Результат закэширован для ключа: {key}")
            return result

    return cache_result
