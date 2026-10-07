"""Small project-local .env loader with shell variables taking precedence."""
from __future__ import annotations

import os
from pathlib import Path

DEFAULT_PAYMENT_METHODS = ('Наличные', 'Kaspi', 'Карта')


def parse_payment_methods(raw: object) -> tuple[str, ...]:
    """Normalize the UI payment-method list while keeping a safe fallback."""
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
    """Load simple KEY=VALUE settings from the project .env if present.

    Existing process variables always win. Relative CYBRAN_DATABASE values from
    the project file are resolved relative to the project root, so launching
    ``run.py`` from another working directory still selects the same SQLite.
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
        if not separator or not key or key in os.environ:
            continue
        value = _value(raw)
        if key == 'CYBRAN_DATABASE' and value and not Path(value).is_absolute():
            value = str((env_path.parent / value).resolve())
        os.environ[key] = value
    return env_path
