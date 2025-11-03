#!/usr/bin/env python3

try:
    # Для случая, когда пакет установлен
    from src.primitive_db.engine import welcome
except ImportError:
    # Для случая разработки
    from .engine import welcome


def main():
    welcome()


if __name__ == '__main__':
    main()