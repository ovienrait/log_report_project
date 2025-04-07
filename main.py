from multiprocessing import Pool
from typing import Any, Dict, List

from core.parsing import parse_args, parse_file
from core.registry import report_registry
from core.reports import Report


def main() -> None:
    """
    Основная функция программы, которая выполняет следующие действия:
    1. Разбирает аргументы командной строки (список логов и имя отчета).
    2. Извлекает класс отчета из реестра отчетов с использованием имени отчета.
    3. Собирает и анализирует данные из логов с использованием многозадачности.
    4. Генерирует и выводит отчет.

    Если указанный отчет или лог не найден, выводится сообщение об ошибке.
    """
    args = parse_args()
    report_class: type[Report] | None = report_registry.get(args.report)
    print()

    if report_class:
        report: Report = report_class()
        try:
            with Pool() as pool:
                parsed_logs_list: List[List[Dict[str, Any]]] = pool.starmap(
                    parse_file, [(log_file, report.log_pattern
                                  ) for log_file in args.log_files])

            parsed_logs: List[Dict[str, Any]] = [
                log for parsed_data in parsed_logs_list for log in parsed_data
            ]

            print(report.generate(parsed_logs))

        except FileNotFoundError:
            exit()


if __name__ == '__main__':
    main()
