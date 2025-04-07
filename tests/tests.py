import os
import re
import sys
import tempfile
from unittest.mock import patch

import pytest

from core.parsing import parse_args, parse_file
from core.registry import report_registry
from core.reports import Report


@pytest.fixture
def fake_report():
    """Фикстура для создания тестового отчета и его регистрации в реестре."""

    class FakeReport(Report):
        display_name = 'test-report'

        def __init__(self) -> None:
            log_pattern = re.compile(
                r'(?P<level>INFO|ERROR) (?P<source>\S+): (?P<endpoint>/\S+)'
            )
            super().__init__(log_pattern)

        def generate(self, data) -> str:
            return 'Test output' + str(data)

    report_registry.reports[FakeReport.display_name] = FakeReport
    fake_report_instance = FakeReport()
    yield FakeReport, fake_report_instance
    del fake_report_instance
    del report_registry.reports[FakeReport.display_name]


@pytest.fixture
def sys_argv(request):
    """Фикстура для имитации передачи аргументов с командой в консоль."""

    with patch.object(sys, 'argv', request.param):
        yield


@pytest.fixture
def log_file():
    """Фикстура для создания тестового лог файла."""

    log_content = (
        "INFO django.request: /api/test\n"
        "ERROR django.request: /api/test\n"
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "test.log")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(log_content)
        yield file_path


def test_report_registry(fake_report):
    """Проверка регистрации отчета в реестре."""

    assert fake_report[1].display_name in report_registry.reports
    assert report_registry.get(fake_report[1].display_name) == fake_report[0]


@pytest.mark.parametrize(
        'sys_argv',
        [['main.py', 'logs/test.log', '--report', 'test-report']],
        indirect=True
    )
def test_parse_args_valid(fake_report, sys_argv):
    """Проверка успешного парсинга валидных аргументов."""

    args = parse_args()
    assert args.log_files == ['logs/test.log']
    assert args.report == 'test-report'


@pytest.mark.parametrize(
        'sys_argv',
        [['main.py', 'logs/test.log', '--report', 'invalid-report-name']],
        indirect=True
    )
def test_parse_args_invalid_report(sys_argv):
    """Проверка ошибки при передаче несуществующего имени отчета."""

    with pytest.raises(SystemExit):
        parse_args()


def test_parse_file_valid(fake_report, log_file):
    """Проверка корректного парсинга лог файла."""

    parsed_data = parse_file(log_file, fake_report[1].log_pattern)
    assert len(parsed_data) == 2
    assert parsed_data[0]['level'] == 'INFO'
    assert parsed_data[0]['source'] == 'django.request'
    assert parsed_data[0]['endpoint'] == '/api/test'


def test_parse_file_invalid_file(fake_report):
    """Проверка обработки ошибки при отсутствии лог файла."""

    with pytest.raises(FileNotFoundError):
        parse_file('nonexistent_file.log', fake_report[1].log_pattern)


def test_report_generate(fake_report, log_file):
    """Проверка вывода отчета."""

    parsed_data = parse_file(log_file, fake_report[1].log_pattern)
    output = fake_report[1].generate(parsed_data)
    assert isinstance(output, str)
    assert len(output) > 0
    assert 'Test output' in output
    assert str(parsed_data) in output
