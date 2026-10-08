# База данных

Рабочее хранилище — SQLite-файл из `CYBRAN_DATABASE`. Каталог создаётся автоматически. В Git не попадают `instance/`, `.env`, ключ сессии и SQLite-файлы.

## Таблицы

- `Users`: логин, имя, роль (`Super Admin`, `Admin`, `Cashier`, `Investor`), активность и `auth_version`.
- `Funds`: фонд, описание, тип `for_stats` или `no_stats`, создатель и признак архива.
- `Rights`: уникальная пара `user_id`/`fund_id`; она ограничивает фонды Admin, Cashier и Investor.
- `Transactions`: доход, расход или перевод. `money` — положительное целое в minor units; направление хранится в `from_fund_id` и `to_fund_id`.
- `ApiTokens`: SHA-256 токена, срок, активность и владелец. Сам секрет в базе не хранится.
- `WebSessions`: хэш cookie, срок, IP, user-agent, версия авторизации и отзыв.
- `LoginAttempts`: хэшированные корзины rate limit, очищаемые по окну времени.

Foreign keys включены для каждого соединения. Ограничения SQLite запрещают неизвестные роли и типы, нулевые суммы, неправильные стороны операции и неполную пару перевода. Индексы покрывают даты операций, направления фондов, Rights и активные сессии.

## Проверки

```powershell
.\.venv\Scripts\python.exe -c "import sqlite3; db=sqlite3.connect('instance/demo.sqlite3'); print(db.execute('PRAGMA integrity_check').fetchone()[0]); print(list(db.execute('PRAGMA foreign_key_check'))); db.close()"
```

Остановите Waitress перед резервным копированием. Не редактируйте рабочие строки вручную: используйте интерфейс или сервисы, чтобы сохранить Rights, пару переводов и аудит доступа.
