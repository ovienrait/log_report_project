from collections import defaultdict
import re
from typing import Any, Dict, List, Optional

from .constants import LOG_LEVELS, LOG_SOURCES, REQUEST_TYPES, ERROR_KEYWORDS


class Report:
    """Абстрактный базовый класс для отчетов."""

    display_name: Optional[str] = None

    def __init__(self, log_pattern: re.Pattern[str]) -> None:
        self.log_pattern = log_pattern

    def generate(self, parsed_logs: List[Dict[str, Any]]) -> str:
        pass


class HandlersReport(Report):
    """Отчет о состоянии ручек API по каждому уровню логирования."""

    display_name: str = 'handlers'

    def __init__(self) -> None:
        log_pattern: re.Pattern[str] = re.compile(
            rf'.* (?P<level>{"|".join(LOG_LEVELS)}) {LOG_SOURCES[0]}: '
            rf'(?:{"|".join(REQUEST_TYPES + ERROR_KEYWORDS[:1])}:)? '
            r'?(?P<endpoint>/\S+)?'
        )
        super().__init__(log_pattern)

    def generate(self, parsed_logs: List[Dict[str, Any]]) -> str:
        endpoint_levels: Dict[Optional[str], Dict[str, int]] = defaultdict(
            lambda: defaultdict(int))
        total_requests: int = 0

        for log in parsed_logs:
            endpoint_levels[log['endpoint']][log['level']] += 1
            total_requests += 1

        report: str = f'\nTotal requests: {total_requests}\n\n'

        report += f'{"HANDLER":<24}'
        for level in LOG_LEVELS:
            report += f'{level:<8}'
        report += '\n'

        sorted_endpoints = sorted(endpoint_levels.keys())

        for endpoint in sorted_endpoints:
            level_counts = endpoint_levels[endpoint]
            report += f'{endpoint:<24}'
            for level in LOG_LEVELS:
                report += f'{level_counts[level]:<8}'
            report += '\n'

        total_by_level: Dict[str, int] = defaultdict(int)
        for level_counts in endpoint_levels.values():
            for level, count in level_counts.items():
                total_by_level[level] += count

        report += f'{"":<24}'
        for level in LOG_LEVELS:
            report += f'{total_by_level[level]:<8}'
        report += '\n'

        return report


class LogsByLevelReport(Report):
    """Отчет об общем количестве логов по каждому уровню логирования."""

    display_name: str = 'logs-by-level'

    def __init__(self) -> None:
        log_pattern: re.Pattern[str] = re.compile(
            rf'.* (?P<level>{"|".join(LOG_LEVELS)}) '
            rf'(?P<source>{"|".join(LOG_SOURCES)}):'
        )
        super().__init__(log_pattern)

    def generate(self, parsed_logs: List[Dict[str, Any]]) -> str:
        level_counts: Dict[str, int] = defaultdict(int)

        for log in parsed_logs:
            level_counts[log['level']] += 1

        report: str = '\nLogs by level\n\n'

        for level in LOG_LEVELS:
            report += f'{level:<10}: {level_counts[level]}\n'

        return report
