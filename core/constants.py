from typing import List

# Константы для формирования шаблонов поиска логов.
# Используются в шаблонах регулярных выражений в отчетах.
LOG_LEVELS: List[str] = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG_SOURCES: List[str] = ['django.request', 'django.security',
                          'django.db.backends', 'django.core.management']
REQUEST_TYPES: List[str] = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE',
                            'HEAD', 'OPTIONS']
ERROR_KEYWORDS: List[str] = ['Internal Server Error', 'OSError']
