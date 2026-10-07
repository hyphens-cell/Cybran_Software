# Архитектура и контракт модулей

Python / Flask / SQLite (`sqlite3`) / Jinja2 / локальный Bootstrap. Никакого SPA.

1. `app/db.py`: соединение на запрос, FK, схема, явные атомарные изменения.
2. `app/auth.py`: session login, CSRF, Bearer token, проверки ролей, `g.user` (dict).
3. `app/services.py`: общая бизнес-логика для HTML и API; суммы только целые minor units.
4. `app/api.py`: исходные URL ТЗ и JSON, bearer-only.
5. `app/web.py`: HTML маршруты; `app/templates/`, `app/static/` — представление.
6. `app/__init__.py`: фабрика `create_app(test_config=None)`, конфигурация и CLI.
7. `tests/`: изолированная SQLite, реальные HTTP запросы Flask client и проверки данных.

Порядок: схема и сервисы → HTML/API → интеграционные тесты → браузер → независимый аудит.

## Контракт для HTML

`from app.auth import login_required, roles_required` — декораторы; роли строго
`Super Admin`, `Admin`, `Cashier`, `Investor`. `g.user` — dict или None.
`from app.db import get_db` — sqlite3.Connection с Row.
`from app import services as svc`; ошибки `svc.DomainError(message, status=400)`.
Все операции записи сервисов сами фиксируют DB-транзакцию.

- `svc.list_funds(user, include_archived=True)` → список dict с полями Funds + balance, transaction_count.
- `svc.fund_detail(user, fund_id)` → такой dict, проверяет доступ к деталям.
- `svc.list_transactions(user, filters=None, global_view=False)` → list dict (одна строка на перевод), поля Transactions + username, fullname, author_role, from_fund_name, to_fund_name. `filters`: date_from/date_to/type/pay_type/fund_id.
- `svc.dashboard(user, filters=None)` → dict: balance, turnover, expenses, net_flow, month_income, month_expense, profit, funds (с income, expense), recent, trend (date, money), distribution (name, balance).
- `svc.create_transaction(user, data)`; `svc.create_transfer(user, data)`; `svc.edit_transaction(user, id, data)`; `svc.delete_transaction(user, id)`; `svc.cancel_last(user, id)`.
- data дохода/расхода: name, description, money (int), type, pay_type, fund_id, datetime (optional ISO).
- data перевода: name, description, money (int), from_fund_id, to_fund_id, pay_type (optional), datetime (optional).
- `svc.can_modify(user, transaction)` → bool для отображения действий.
- `svc.last_cashier_transaction_id(user)` → id или None.
- `svc.list_users(user, search='', role='')`; `svc.create_user(user,data)`; `svc.edit_user(user,id,data)`; `svc.block_user(user,id,is_active)`; `svc.reset_password(user,id,password)`.
- `svc.create_fund(user,data)`; `svc.edit_fund(user,id,data)`; `svc.archive_fund(user,id)`.
- `svc.list_rights(user)` → список {id,user_id,fund_id}; `svc.grant_right(user,user_id,fund_id)`; `svc.revoke_right(user,user_id,fund_id)`; `svc.set_rights(user,user_id,fund_ids)` атомарная матрица.
- `svc.list_tokens(user)` → безопасные id, user_id, username, active, datetime.
- `svc.create_token(user,user_id)` → dict {id, token, user_id}; `svc.revoke_token(user,id)`.
- `svc.export_rows(user,filters=None)` → список безопасных dict для for_stats; `svc.export_file(user,filters,format)` → (bytes, mimetype, filename).

В шаблоны доступны `current_user`, `csrf_token()`; все HTML POST должны содержать `csrf_token`.
В API роли Cashier и Investor не перечислены исходной таблицей, поэтому API возвращает им 403; их HTML возможности реализованы отдельно. HTML login/logout реализует `app/auth.py`: endpoints `auth.login`, `auth.logout`. После входа переход на `web.index`. Ошибки через общий шаблон `error.html` (переменные code,message).

Деньги в форме HTML переводить через `Decimal` в int minor units (никаких float), отображение через фильтр `money` (создает основной агент). Экспорт формирует основной агент. Защита CSRF централизована.
