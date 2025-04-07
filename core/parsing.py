import argparse
import re
from typing import Any, Dict, List

from .registry import report_registry


class CustomArgumentParser(argparse.ArgumentParser):
    """Кастомный парсер для обработки ошибок в случае неверного типа отчета."""

    def error(self, message: str) -> None:
        print('\nУказанный тип отчёта отсутствует.',
              f'Доступные отчёты: {", ".join(report_registry.reports.keys())}')
        exit()


def parse_args() -> argparse.Namespace:
    """Обработчик для парсинга аргументов командной строки."""

    parser: argparse.ArgumentParser = CustomArgumentParser()
    parser.add_argument('log_files', nargs='+')
    parser.add_argument('--report', choices=report_registry.reports.keys())
    return parser.parse_args()


def parse_file(
    log_file: str, log_pattern: re.Pattern[str]
) -> List[Dict[str, Any]]:
    """Обработчик для парсинга файла лога."""

    parsed_data: List[Dict[str, Any]] = []
    try:
        with open(log_file, 'r', encoding='utf-8') as file:
            for line in file:
                match: re.Match[str] | None = log_pattern.search(line)
                if match:
                    parsed_data.append(match.groupdict())
    except FileNotFoundError:
        print(f'Файл {log_file} не найден.')
        raise
    return parsed_data
