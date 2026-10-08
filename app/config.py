"""Небольшой загрузчик локального `.env` с приоритетом переменных процесса."""
from __future__ import annotations

import os
from pathlib import Path

DEFAULT_PAYMENT_METHODS = ('Наличные', 'Kaspi', 'Карта')
PROJECT_ENV_KEYS = frozenset({
    'CYBRAN_DATABASE', 'PAYMENT_METHODS', 'HOST', 'PORT', 'MOBILE_IP',
    'COOKIE_SECURE', 'SECRET_KEY', 'TRUSTED_PROXY_HOPS',
})


def parse_payment_methods(raw: object) -> tuple[str, ...]:
    """Нормализовать способы оплаты для интерфейса и сохранить запасной список."""
    if isinstance(raw, str):
        values = raw.split(',')
    elif isinstance(raw, (list, tuple)):
        values = raw
    else:
        values = DEFAULT_PAYMENT_METHODS
    result = tuple(dict.fromkeys(str(value).strip() for value in values if str(value).strip()))
    return result or DEFAULT_PAYMENT_METHODS


def _value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def load_project_env(path: str | Path | None = None) -> Path | None:
    """Загрузить простые настройки KEY=VALUE из `.env`, если файл существует.

    Переменные процесса всегда имеют приоритет. Относительный путь
    `CYBRAN_DATABASE` вычисляется от корня проекта, поэтому запуск `run.py`
    из другой папки всё равно выбирает ту же SQLite-базу.
    """
    env_path = Path(path) if path is not None else Path(__file__).resolve().parent.parent / '.env'
    if not env_path.is_file():
        return None
    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:].lstrip()
        key, separator, raw = line.partition('=')
        key = key.strip()
        if not separator or not key or key not in PROJECT_ENV_KEYS or key in os.environ:
            continue
        value = _value(raw)
        if key == 'CYBRAN_DATABASE' and value and not Path(value).is_absolute():
            value = str((env_path.parent / value).resolve())
        os.environ[key] = value
    return env_path
