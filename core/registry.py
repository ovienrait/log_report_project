import inspect
import types
from typing import Dict, Optional

import core.reports as reports

from .reports import Report


class ReportRegistry:
    """Реестр отчетов. Позволяет регистрировать и извлекать отчеты по имени."""

    def __init__(self) -> None:
        self.reports: Dict[str, type[Report]] = {}

    def register(self, module: types.ModuleType) -> None:
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Report) and (
                obj.display_name is not None
            ):
                self.reports[obj.display_name] = obj

    def get(self, report_name: str) -> Optional[type[Report]]:
        return self.reports.get(report_name)


report_registry: ReportRegistry = ReportRegistry()
report_registry.register(reports)
