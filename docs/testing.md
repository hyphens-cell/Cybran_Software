# Проверка

## Основной прогон

```powershell
New-Item -ItemType Directory -Force tmp
.\.venv\Scripts\python.exe -m pytest -q --basetemp=tmp/pytest_release
.\.venv\Scripts\python.exe -m compileall -q app tests run.py
.\.venv\Scripts\python.exe -m flask --app app routes
```

`--basetemp` направляет временные файлы внутрь проекта. Это нужно на компьютерах, где системный `%TEMP%` закрыт политиками доступа. Тесты создают независимые SQLite-файлы и не меняют `instance/`.

## Что покрыто

Проверяются роли и Rights, запрет блокировки самого себя, CSRF, IDOR, rate limit, срок и отзыв API-токена, серверные сессии, целостность переводов, балансы, архивы, `for_stats`/`no_stats`, отчёты CSV/XLSX, мобильный QR, конфигурация `.env` и настраиваемые способы оплаты.

## Дополнительный аудит

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-audit.txt
.\.venv\Scripts\bandit.exe -r app run.py -x .venv,tmp,.git,tests
.\.venv\Scripts\pip-audit.exe -r requirements.txt
```

Если Semgrep или pip-audit недоступны в изолированной среде, зафиксируйте это в `docs/security-audit.md`, а не объявляйте проверку пройденной.
