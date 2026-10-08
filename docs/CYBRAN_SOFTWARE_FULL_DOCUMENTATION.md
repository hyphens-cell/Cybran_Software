# Полная документация Cybran Software

<a id="full-documentation"></a>

Единый сборник документации проекта. Исходные файлы сохранены отдельно; этот файл объединяет их актуальное содержимое для удобного чтения и передачи.

Сборник сформирован: 2026-10-08.

## Содержание

1. [`README.md`](#readmemd)
2. [`REQUIREMENTS_CHECKLIST.md`](#requirements-checklistmd)
3. [`SECURITY_CHECKLIST.md`](#security-checklistmd)
4. [`SECURITY_REPORT.md`](#security-reportmd)
5. [`docs/api.md`](#docs-apimd)
6. [`docs/architecture.md`](#docs-architecturemd)
7. [`docs/backup-and-restore.md`](#docs-backup-and-restoremd)
8. [`docs/configuration.md`](#docs-configurationmd)
9. [`docs/database.md`](#docs-databasemd)
10. [`docs/DECISIONS.md`](#docs-decisionsmd)
11. [`docs/deployment.md`](#docs-deploymentmd)
12. [`docs/financial-logic.md`](#docs-financial-logicmd)
13. [`docs/installation.md`](#docs-installationmd)
14. [`docs/MANUAL_TEST_PLAN.md`](#docs-manual-test-planmd)
15. [`docs/operations.md`](#docs-operationsmd)
16. [`docs/release-audit.md`](#docs-release-auditmd)
17. [`docs/repository-cleanup.md`](#docs-repository-cleanupmd)
18. [`docs/roles-and-permissions.md`](#docs-roles-and-permissionsmd)
19. [`docs/security-audit.md`](#docs-security-auditmd)
20. [`docs/SIMPLE_MANUAL_CHECK.md`](#docs-simple-manual-checkmd)
21. [`docs/testing.md`](#docs-testingmd)
22. [`docs/troubleshooting.md`](#docs-troubleshootingmd)
23. [`docs/VERIFICATION.md`](#docs-verificationmd)

---

<a id="readmemd"></a>
## Раздел 1: `README.md`

Исходный файл: [`README.md`](../README.md)

# Cybran Software CRM

## О проекте

CRM учёта финансов по фондам. Система хранит операции в минорных единицах, применяет роли и Rights, показывает отчётность и предоставляет защищённый REST API. Требования сверяются с исходным PDF в [REQUIREMENTS_CHECKLIST.md](#requirements-checklistmd), решения по противоречиям — в [docs/DECISIONS.md](#docs-decisionsmd).

## Возможности

- отдельные сценарии для Super Admin, Admin, Cashier и Investor;
- фонды, архивирование, Rights, доходы, расходы и атомарные межфондовые переводы;
- сводка `for_stats`, исключение `no_stats`, CSV/XLSX и мобильный запуск с QR;
- браузерные сессии, API-токены, аудит действий и серверная проверка прав.

## Технологический стек

Python 3.12+, Flask, SQLite, Jinja2, Bootstrap, HTML/CSS, минимальный vanilla JavaScript и Waitress. Bootstrap хранится локально, внешние CDN не требуются.

## Требования

Нужны Python 3.12 или новее и PowerShell в Windows либо эквивалентный shell в другой ОС. Для разработки используется виртуальное окружение `.venv`.

Для быстрой проверки без технических терминов используйте [docs/SIMPLE_MANUAL_CHECK.md](#docs-simple-manual-checkmd). Полная пошаговая приемка от чистой базы до проверки ролей, финансов, API, отчетов и мобильного QR находится в [docs/MANUAL_TEST_PLAN.md](#docs-manual-test-planmd). Результаты аудита безопасности собраны в [SECURITY_REPORT.md](#security-reportmd), а контрольный список — в [SECURITY_CHECKLIST.md](#security-checklistmd).

## Быстрый запуск

Скопируйте `.env.example` в `.env` и измените `CYBRAN_DATABASE`, если нужно выбрать другую SQLite-базу. В текущем рабочем окружении `.env` уже указывает на `instance/demo.sqlite3`. Путь можно задавать относительным к корню проекта или абсолютным. Переменная, заданная в PowerShell, имеет приоритет над `.env`; это позволяет временно проверить другую базу без редактирования файла.

## Конфигурация

Список быстрых способов оплаты на экранах кассира, операции и фильтров задаётся в `.env` через `PAYMENT_METHODS=Наличные,Kaspi,Карта`. После изменения перезапустите `run.py`. Поле API и ручной ввод операции по-прежнему принимают любой непустой способ оплаты до 50 символов, как разрешено ТЗ; параметр управляет именно подсказками и кнопками интерфейса.

Подробное описание переменных находится в [docs/configuration.md](#docs-configurationmd), а пошаговая установка — в [docs/installation.md](#docs-installationmd).

## Инициализация базы данных

После установки зависимостей выполните:

```powershell
.\.venv\Scripts\python.exe -m flask --app app init-db
```

Команда создаёт SQLite-файл и таблицы идемпотентно; существующие записи не удаляются.

## Создание первого Super Admin

```powershell
.\.venv\Scripts\python.exe -m flask --app app create-superadmin
```

Команда запрашивает логин, имя и пароль. В исходниках нет предустановленного пароля.

## Запуск

Нужен Python 3.12+. Зависимости приложения устанавливаются в виртуальное окружение проекта.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app init-db
.\.venv\Scripts\python.exe -m flask --app app create-superadmin
.\.venv\Scripts\python.exe run.py
```

После запуска терминал показывает выбранный путь `SQLite база: ...`, адрес для телефона и QR-код. Телефон и компьютер должны находиться в одной локальной сети; наведите камеру на QR-код. Адрес вида `http://192.168.x.x:5000` зависит от вашей сети. Если телефон подключен к мобильной точке Windows, можно выбрать её адрес через `MOBILE_IP=192.168.137.1` в `.env` или `$env:MOBILE_IP = '192.168.137.1'` перед запуском. Команда создания Super Admin запрашивает логин и пароль. В исходниках нет предустановленного пароля. SQLite автоматически создаётся при первом запуске; повторный `init-db` сохраняет данные. В этом рабочем окружении `.venv` уже подготовлено, поэтому первые два шага повторять не требуется.

На текущем компьютере создано правило Windows Firewall `Cybran Software Mobile`: TCP-порт 5000 разрешен только для локальной сети `192.168.0.0/19` и мобильной точки `192.168.137.0/24`, только в профилях Domain/Private. Удалить правило после окончания работы можно из PowerShell администратора: `netsh advfirewall firewall delete rule name="Cybran Software Mobile"`.

Приложение запускается через Waitress без debug/reloader. Для мобильного доступа оно слушает локальные интерфейсы (`0.0.0.0`); `HOST=127.0.0.1` возвращает режим «только этот компьютер», а `PORT` меняет порт. Это подключение предназначено для доверенной локальной сети, не для публикации в интернете. Для публичного размещения используйте HTTPS reverse proxy, установите `COOKIE_SECURE=1`, `TRUSTED_PROXY_HOPS` ровно в число собственных proxy-hop и собственный `SECRET_KEY`. Backend должен быть недоступен клиентам в обход этого proxy; иначе forwarded-заголовки нельзя считать доверенными. Не используйте Flask debug в публичном окружении.

## Демонстрационная база

```powershell
# Если .env уже указывает на demo.sqlite3, достаточно этой команды:
.\.venv\Scripts\python.exe run.py
```

Чтобы явно переопределить базу только для текущего окна PowerShell:

```powershell
$env:CYBRAN_DATABASE = Join-Path (Get-Location) 'instance\demo.sqlite3'
```

`run.py` печатает фактически выбранный путь `SQLite база: ...` в терминале. Если `.env` отсутствует и переменная не задана, используется `instance\cybran.sqlite3`.

`seed-demo` работает только с пустой базой и создаёт четыре роли, четыре фонда, пример истории и перевод. Простые пароли для локальной демонстрации сохраняются в `instance/demo-access.txt`; использовать их в рабочей базе нельзя. Это демонстрационные операции. Для собственной чистой базы уберите переменную `CYBRAN_DATABASE`, выполните `create-superadmin` и запустите сервер заново. Демоданные автоматически при запуске не добавляются.

## Возможности по ролям

- **Super Admin:** сводка, все фонды/операции, пользователи, роли, блокировка, сброс пароля, матрица прав, API-токены, активные browser-сессии и настройки участия фондов в отчётности. Можно завершить выбранную сессию, все остальные или все сразу. Собственную учётную запись нельзя заблокировать или понизить в роли; система всегда сохраняет хотя бы одного активного Super Admin.
- **Admin:** баланс и история фондов из Rights, доходы/расходы, перевод между двумя своими фондами, исправление своих операций и операций кассиров.
- **Cashier:** быстрая форма оплаты, расход, история доступных фондов и смен по дням, отмена только своей последней операции.
- **Investor:** сводка всех `for_stats`, CSV/Excel за период; отдельная история доступна для `for_stats` с Rights. `no_stats` и недоступные стороны переводов скрыты.

Сумма в HTML-форме вводится в основных единицах с двумя десятичными знаками (например, `1250,50`); в БД и API это `125050` minor units. Валюту система не назначает. Время операций хранится в UTC, границы дат включают весь выбранный день. Баланс — текущий; оборот/расход/чистый поток — за выбранный период; месячные показатели — за текущий месяц. Отрицательные остатки разрешены, так как запрета в ТЗ нет.

Перевод — две связанные записи `inter-transaction`, одна уменьшает источник, другая увеличивает получателя. В UI/экспорте это одна операция. Изменение/удаление любого ID пары меняет обе записи атомарно. Переводы не включаются во внешние доходы/расходы. Архив фонда сохраняет историю и остатки, запрещает новые операции; Super Admin может исправлять прошлые записи.

## REST API

Все обязательные endpoints сохранены. Токен генерируется только в интерфейсе Super Admin → API-токены, показывается один раз, хранится в БД как SHA-256 и действует 30 дней. Каждый запрос передаёт `Authorization: Bearer <128-символьный токен>`; cookie-сессия для API не подходит. Владелец определяет роль и Rights; отзыв токена, блокировка владельца и сброс его пароля действуют немедленно.

| Метод | Путь | Роли |
|---|---|---|
| POST | `/api/create_user` | Super Admin |
| PUT | `/api/users/{id}/edit_user` | Super Admin |
| PATCH | `/api/users/{id}/block` | Super Admin |
| POST | `/api/create_fund` | Super Admin |
| PATCH | `/api/funds/{id}/archive` | Super Admin |
| POST | `/api/rights` | Super Admin |
| DELETE | `/api/rights/{user_id}/{fund_id}` | Super Admin |
| DELETE | `/api/tokens/{id}` | Super Admin |
| PUT / DELETE | `/api/transactions/{id}` | Super Admin |
| GET | `/api/funds` | Admin, Super Admin |
| POST | `/api/transactions/add` | Admin, Super Admin |
| POST | `/api/transactions/add_transfer` | Admin, Super Admin |
| GET | `/api/transactions` | Admin, Super Admin |
| PUT | `/api/transactions/{id}/edit` | Admin, Super Admin |
| DELETE | `/api/transactions/{id}/delete` | Admin, Super Admin |

Cashier/Investor не перечислены в API-таблицах PDF и получают 403 на эти endpoints. Их функции доступны в защищённом веб-интерфейсе. Это не ограничивает право Super Admin генерировать токен для любого активного пользователя.

Пример JSON для дохода/расхода:

```json
{"fund_id":1,"type":"income","money":125050,"pay_type":"Kaspi","name":"Оплата","description":"Комментарий"}
```

Для перевода: `from_fund_id`, `to_fund_id`, `money`, необязательные `name`, `description`, `pay_type`, `datetime` ISO 8601. Для редактирования можно передать только изменяемые поля. Для смены фонда обычной операции используется `fund_id`.

Создание пользователя: `username`, `fullname`, `role` (точно `Super Admin`, `Admin`, `Cashier`, `Investor`), `password` (8–256 символов). Изменение пользователя принимает эти же поля; пароль необязателен. Блокировка: `{"is_active":false}`, разблокировка: `true`. Создание фонда: `name`, `description`, `type` (`for_stats`/`no_stats`). Rights: `user_id`, `fund_id`.

GET истории поддерживает `date_from`, `date_to` (`YYYY-MM-DD`), `type`, `pay_type`, `fund_id`. Список возвращает JSON array; создание/изменение — объект. Ответы: 201 создание, 200 чтение/изменение, 204 удаление/отзыв, 400 валидация, 401 неверный токен, 403 роль/Rights, 404 отсутствующая запись, 409 конфликт/архив, 415 неверный Content-Type. Ошибки: `{"error":"описание"}`. Все денежные значения JSON — integer, строки/bool/float не принимаются.

## Тестирование

```powershell
New-Item -ItemType Directory -Force tmp
.\.venv\Scripts\python.exe -m pytest -q --basetemp=tmp/pytest
.\.venv\Scripts\python.exe -m compileall -q app tests run.py
.\.venv\Scripts\python.exe -m flask --app app routes
.\.venv\Scripts\python.exe -m pip install -r requirements-audit.txt
.\.venv\Scripts\bandit.exe -r app run.py -x .venv,tmp,.git,tests
.\.venv\Scripts\pip-audit.exe -r requirements.txt
```

Тесты используют отдельные временные SQLite-файлы и не меняют рабочую базу. Проверяются роли, IDOR, CSRF, 24-часовые server-side сессии и их отзыв, ограничение попыток входа, срок/отзыв токенов, финансовые балансы, откат второй записи перевода, отчётность и экспорты.

## Документация

- [Единый сборник документации](#full-documentation);
- [Установка](#docs-installationmd), [конфигурация](#docs-configurationmd), [архитектура](#docs-architecturemd) и [база данных](#docs-databasemd);
- [роли и права](#docs-roles-and-permissionsmd), [финансовая логика](#docs-financial-logicmd) и [REST API](#docs-apimd);
- [тестирование](#docs-testingmd), [операции](#docs-operationsmd), [резервное копирование](#docs-backup-and-restoremd) и [устранение неполадок](#docs-troubleshootingmd);
- [очистка репозитория](#docs-repository-cleanupmd), [аудит безопасности](#docs-security-auditmd) и [контрольный аудит релиза](#docs-release-auditmd).

Простая ручная проверка описана в [docs/SIMPLE_MANUAL_CHECK.md](#docs-simple-manual-checkmd), полный сценарий — в [docs/MANUAL_TEST_PLAN.md](#docs-manual-test-planmd).

## Deployment

Для production используйте [docs/deployment.md](#docs-deploymentmd): HTTPS reverse proxy, отдельный `SECRET_KEY`, `COOKIE_SECURE=1`, ограниченный доступ к backend и резервное копирование по [docs/backup-and-restore.md](#docs-backup-and-restoremd).

## Проверка и устройство

`app/db.py` — схема и транзакции; `services.py` — бизнес-правила; `auth.py` — аутентификация; `api.py` — REST; `web.py` — HTML; `templates/` и `static/` — интерфейс; `tests/` — интеграционная проверка. Bootstrap хранится локально, внешних CDN приложение не требует. Логотип предоставлен пользователем.

Рабочая база и ключ подписи cookie находятся в `instance/` (исключено из Git). Для резервной копии остановите сервер и скопируйте SQLite вместе с ключом либо используйте SQLite backup API. Browser-cookie содержит случайный идентификатор; в SQLite хранится только его SHA-256. Сессия завершается через 24 часа после входа независимо от активности, а logout и отзыв Super Admin прекращают её на сервере сразу. Пароль хранится как PBKDF2-HMAC-SHA256 с солью, Bearer-токен — SHA-256. В CSV защищены пользовательские формулы; в XLSX текст сохраняется текстом, целые числа свыше 15 цифр — строками без потери точности Excel.

---

<a id="requirements-checklistmd"></a>
## Раздел 2: `REQUIREMENTS_CHECKLIST.md`

Исходный файл: [`REQUIREMENTS_CHECKLIST.md`](../REQUIREMENTS_CHECKLIST.md)

# Cybran Software — соответствие техническому заданию

Основной источник бизнес-требований: **«ТЗ для Бубелиса Йонаса.pdf», 10 страниц**. Все страницы прочитаны полностью. Номера страниц ниже относятся к исходному PDF. Дополнительные требования к стеку, безопасности, проверке и поставке взяты из пользовательского `goal-objective.md`; они обозначены `Цель §N` и не выдаются за содержание PDF.

Три независимых статуса в каждой строке: **Требование** — извлечено и сверено с источником; **Реализация** — проверена в коде; **Проверка** — получено свидетельство работоспособности. Наличие текста сценария проверки само по себе не означает, что тест существует или проходит. Незакрытые статусы нельзя считать завершенной работой. Решения по неоднозначностям находятся в [docs/DECISIONS.md](#docs-decisionsmd).

## 1. Назначение, архитектура и данные

| ID | Источник | Требование | Реализация | Проверка / критерий приемки |
|---|---|---|---|---|
| BASE-01 | PDF 1 | [x] Веб-приложение «Cybran Software» ведет деньги по изолированным фондам; видны фонд, сумма, направление, автор и способ движения. | [x] `app/services.py:create_transaction,list_transactions; app/templates/components/transactions_table.html`. | [x] `test_api.py:test_income_expense_and_integer_balances; test_fund_and_transaction_lists_are_scoped`. Критерий: Доход/расход видны в правильном фонде с автором и pay_type; чужие фонды не раскрываются. |
| BASE-02 | PDF 1, 4, 10; Цель §9, 17–18 | [x] Python + Flask + SQLite + Jinja2 + Bootstrap, HTML/CSS, минимальный vanilla JS; модульное приложение, веб-интерфейс и REST API. | [x] `app/__init__.py:create_app; app/db.py:init_db; requirements.txt; app/templates/base.html`. | [x] `test_management.py:test_required_schema_columns_exist; tests/conftest.py:app (170 изолированных запусков фабрики)`. Критерий: Чистая установка, создание SQLite и запуск; отсутствие заменяющего backend/frontend стека и обязательных внешних сервисов. |
| DB-01 | PDF 3 | [x] Users: id, username str(50), fullname str(150), password_hash str(256), role str(50), связь Rights. | [x] `app/db.py:SCHEMA — Users; app/services.py:create_user`. | [x] `test_management.py:test_required_schema_columns_exist; test_create_users_all_roles_and_no_password_leak`. Критерий: Поля/ограничения/связи существуют; пароль хранится только как хэш. |
| DB-02 | PDF 3, 5, 8 | [x] Users.is_active поддерживает блокировку и разблокировку. | [x] `app/auth.py:load_user,authenticate_api; app/services.py:block_user`. | [x] `test_auth_rbac.py:test_blocked_user_invalidates_login_session_and_api`. Критерий: После блокировки не работают новый вход, текущая сессия и API-токен. |
| DB-03 | PDF 3 | [x] Rights: id, fund_id → Funds, user_id → Users. | [x] `app/db.py:SCHEMA — Rights; app/services.py:grant_right,revoke_right`. | [x] `test_management.py:test_database_constraints_enforce_relationships_and_types; test_grant_revoke_right_changes_existing_token_immediately`. Критерий: Выданное право дает доступ; отзыв немедленно его убирает; некорректные ссылки не создаются. |
| DB-04 | PDF 3, 5, 9 | [x] ApiTokens: id, token с SHA-256-хэшем, active/is_active, datetime создания, user_id владельца. | [x] `app/db.py:SCHEMA — ApiTokens; app/services.py:create_token,revoke_token`. | [x] `test_management.py:test_required_schema_columns_exist; test_token_generated_once_hash_only_and_revocation`. Критерий: Открытого токена нет в БД; хэш связан с правильным владельцем; отзыв сохраняет запись, но запрещает доступ. |
| DB-05 | PDF 3, 5, 8 | [x] Funds: id, name str(50), description str(150), type for_stats/no_stats, user_id создателя, связи с Transactions, is_active для архива. | [x] `app/db.py:SCHEMA — Funds; app/services.py:archive_fund`. | [x] `test_management.py:test_create_edit_archive_fund_and_metadata; test_integrity.py:test_archiving_preserves_history_balances_and_global_stats`. Критерий: Оба типа допустимы, другие отвергаются; архивирование сохраняет фонд и финансовую историю. |
| DB-06 | PDF 3–4 | [x] Transactions: id, name str(50), description str(150), money int, type, pay_type str(50), datetime, from_fund_id, to_fund_id, user_id. | [x] `app/db.py:SCHEMA — Transactions`. | [x] `test_management.py:test_required_schema_columns_exist; test_database_constraints_enforce_relationships_and_types`. Критерий: Все поля/ссылки существуют; типы ограничены income/expense/inter-transaction. |
| DB-07 | PDF 4, 8; Цель §9 | [x] Деньги хранятся и передаются в minor units как INTEGER/int, без float. | [x] `app/db.py:SCHEMA; app/services.py:integer,ledger; app/web.py:minor_units`. | [x] `test_api.py:test_invalid_money_cannot_create_or_edit; test_income_expense_and_integer_balances; test_auth_rbac.py:test_html_money_rejects_non_finite_fractional_or_overflow`. Критерий: Суммы и KPI остаются целыми; дробные JSON numbers, bool и некорректные суммы отвергаются без изменения БД. |

## 2. Аутентификация и разграничение доступа

| ID | Источник | Требование | Реализация | Проверка / критерий приемки |
|---|---|---|---|---|
| AUTH-01 | PDF 4 | [x] Вход по username/password, проверка хэша, определение role и загрузка Rights. | [x] `app/auth.py:login,load_user`. | [x] `test_auth_rbac.py:test_login_role_landing_and_logout; test_bad_password_and_csrf`. Критерий: Верный вход успешен, неверные данные отклонены; пароль/хэш не попадают в ответ. |
| AUTH-02 | Цель §21 | [x] Выход завершает пользовательскую сессию. | [x] `app/auth.py:logout`. | [x] `test_auth_rbac.py:test_login_role_landing_and_logout`. Критерий: После выхода защищенный маршрут не открывается прежней сессией. |
| AUTH-03 | PDF 2, 4; Цель §4 | [x] Ровно четыре роли: Super Admin, Admin, Cashier, Investor; панель зависит от роли. | [x] `app/services.py:ROLES,require_role; app/web.py:index`. | [x] `test_auth_rbac.py:test_login_role_landing_and_logout; test_management.py:test_create_users_all_roles_and_no_password_leak`. Критерий: Каждая роль получает свою панель; неизвестная роль не создается. |
| AUTH-04 | PDF 2, 5–6, 9; Цель §4, 19 | [x] Все права проверяются backend; подмена URL, fund_id или формы не обходит Rights/роль. | [x] `app/services.py:require_fund,_require_modify; app/auth.py:roles_required`. | [x] `test_auth_rbac.py:test_html_foreign_fund_idor; test_integrity.py:test_transfer_edit_checks_old_and_new_funds; test_api.py:test_author_cannot_be_spoofed_by_client`. Критерий: Прямые HTTP/API запросы к чужому фонду/записи запрещены, включая изменение source/target у существующего перевода. |
| AUTH-05 | PDF 8 | [x] Если роль не перечислена для API endpoint, ответ 403; Super Admin может все endpoints. | [x] `app/api.py:roles and all 16 method/path registrations`. | [x] `test_api.py:test_super_admin_api_role_matrix; test_admin_api_does_not_inherit_cashier_or_investor_ui_rights`. Критерий: Матрица ролей проверена для всех 16 методов/путей; Cashier/Investor не получают Admin API через свои UI-права. |
| AUTH-06 | Цель §19 | [x] HTML-формы защищены от CSRF, SQL-инъекций, некорректного ввода и раскрытия password/token hashes. | [x] `app/auth.py:load_user; app/services.py:text_value,_public_user; параметризованный sqlite3, Jinja autoescape`. | [x] `test_auth_rbac.py:test_bad_password_and_csrf; test_management.py:test_untrusted_html_is_escaped_and_sql_text_is_data; test_token_generated_once_hash_only_and_revocation`. Критерий: POST без CSRF не проходит; SQL-подобные строки безопасны; HTML экранируется; хэшей нет в JSON/страницах/выгрузках. |
| AUTH-07 | Запрос пользователя 2026-10-08; PDF 5, 8 не задаёт исключение | [x] Super Admin не может заблокировать себя, понизить собственную роль или оставить систему без активного Super Admin; HTML принимает только явный флаг статуса. | [x] `app/services.py:_protect_superadmin_access,edit_user,block_user; app/web.py:user_block; app/templates/users.html,user_form.html`. | [x] `test_management.py:test_super_admin_cannot_block_or_downgrade_own_account; test_html_block_requires_explicit_boolean_flag; test_active_super_admin_invariant_survives_stale_concurrent_actor`. Критерий: HTML/API возвращают 409 на self-lockout, ошибочный статус — 400 без мутации, хотя бы один активный Super Admin сохраняется. |
| AUTH-08 | Запрос пользователя 2026-10-08 | [x] Browser-сессии управляются на сервере, отзываются при logout и автоматически заканчиваются через 24 часа без продления активностью; вход ограничен по частоте. | [x] `app/auth.py:create_web_session,load_user,logout,_login_rate_limited; app/db.py:WebSessions,LoginAttempts`. | [x] `tests/test_sessions.py; test_auth_rbac.py:test_login_rate_limit_returns_retry_after,test_unknown_user_uses_dummy_password_hash,test_unknown_usernames_do_not_grow_rate_limit_table`. Критерий: копия cookie не работает после logout/revoke/expiry; шестая попытка пары IP/account получает 429; неизвестные логины не раздувают таблицу. |

## 3. Super Admin

| ID | Источник | Требование | Реализация | Проверка / критерий приемки |
|---|---|---|---|---|
| SA-01 | PDF 4–5 | [x] Список пользователей с поиском и фильтром по роли. | [x] `app/web.py:users; app/services.py:list_users; app/templates/users.html`. | [x] `test_management.py:test_user_edit_search_filter_password_reset_and_invalidation`. Критерий: Поиск и фильтр возвращают ожидаемых пользователей. |
| SA-02 | PDF 2, 4–5, 8 | [x] Создание пользователя любой из четырех ролей, редактирование данных и смена роли. | [x] `app/services.py:create_user,edit_user; app/api.py:create_user,edit_user; app/web.py:user_form`. | [x] `test_management.py:test_create_users_all_roles_and_no_password_leak; test_auth_rbac.py:test_session_and_api_permissions_refresh_after_role_change`. Критерий: Созданы все роли; изменения сохранены; следующий запрос применяет новую роль. |
| SA-03 | PDF 5, 8 | [x] Блокировка/разблокировка пользователя и сброс пароля. | [x] `app/services.py:block_user,reset_password; app/web.py:user_block,user_password`. | [x] `test_auth_rbac.py:test_blocked_user_invalidates_login_session_and_api; test_management.py:test_user_edit_search_filter_password_reset_and_invalidation; test_edit_user_rejects_explicit_invalid_password`. Критерий: Старый пароль после сброса неверен, новый работает; active-состояние учитывается во всех способах входа; явно переданный некорректный пароль отклоняется без ложного успеха. |
| SA-04 | PDF 2, 5, 8 | [x] Создание, редактирование и архивирование фондов без потери истории. | [x] `app/services.py:create_fund,edit_fund,archive_fund; app/web.py:fund_form,fund_archive`. | [x] `test_management.py:test_create_edit_archive_fund_and_metadata; test_integrity.py:test_archiving_preserves_history_balances_and_global_stats`. Критерий: Название/описание/type изменяются; архив не удаляет транзакции и их влияние на баланс. |
| SA-05 | PDF 2, 5, 8–9 | [x] Матрица User ↔ Fund: назначение и отзыв прав, в том числе массовая выдача кассиру нескольких фондов. | [x] `app/services.py:set_rights,grant_right,revoke_right; app/web.py:rights`. | [x] `test_management.py:test_mass_rights_form_and_invalid_replacement_are_atomic; test_grant_revoke_right_changes_existing_token_immediately`. Критерий: Выдача нескольких связей одной формой; отзыв доступа отражается в следующем запросе пользователя. |
| SA-06 | PDF 2, 5 | [x] Для каждого фонда переключается for_stats/no_stats. | [x] `app/services.py:edit_fund; app/web.py:fund_form`. | [x] `test_reporting.py:test_fund_reporting_switch_immediately_changes_dashboard_and_export`. Критерий: Переключение немедленно меняет Global Dashboard и отчеты без удаления данных. |
| SA-07 | PDF 2, 5, 9 | [x] Глобальный аудит: все транзакции всех фондов, изменение любой записи, удаление ошибочной с пересчетом балансов. | [x] `app/services.py:list_transactions,edit_transaction,delete_transaction; app/web.py:transactions`. | [x] `test_api.py:test_global_edit_delete_all_authors; test_integrity.py:test_super_admin_corrects_archived_history_without_enabling_new_entries`. Критерий: Super Admin видит no_stats и чужие записи, исправляет их; баланс и отчетность сразу соответствуют данным. |
| SA-08 | PDF 1–2, 5 | [x] Только Super Admin генерирует 128-символьные безопасные API-токены, видит список активных токенов с владельцем и отзывает их. | [x] `app/services.py:create_token,list_tokens,revoke_token; app/web.py:tokens,token_revoke`. | [x] `test_auth_rbac.py:test_non_super_admin_cannot_open_management; test_management.py:test_token_generated_once_hash_only_and_revocation; test_token_uniqueness_and_blocked_owner`. Критерий: Остальным ролям прямой запрос генерации/списка/отзыва запрещен; active list не раскрывает хэши. |
| SA-09 | Запрос пользователя 2026-10-08 | [x] Super Admin видит активные сессии и может завершить одну, все остальные либо все, включая текущую. | [x] `app/services.py:list_web_sessions,revoke_web_session,revoke_all_web_sessions; app/web.py:sessions,session_revoke,sessions_revoke_all; app/templates/sessions.html`. | [x] `tests/test_sessions.py` — 7 сценариев. Критерий: не-Super Admin получает 403; отзыв немедленно прекращает выбранный вход; режим «остальные» сохраняет текущий, режим «все» завершает и его; идентификатор/hash не раскрывается. |

## 4. Admin

| ID | Источник | Требование | Реализация | Проверка / критерий приемки |
|---|---|---|---|---|
| ADM-01 | PDF 2, 5, 9 | [x] Дашборд содержит только фонды из Rights с текущим балансом и количеством транзакций. | [x] `app/services.py:list_funds,fund_info,ledger; app/web.py:funds`. | [x] `test_api.py:test_fund_and_transaction_lists_are_scoped; test_integrity.py:test_transfer_has_two_rows_and_one_logical_history_entry`. Критерий: Чужих фондов/сумм нет; баланс и счетчик совпадают с историей своего фонда. |
| ADM-02 | PDF 2, 5, 9 | [x] Доход и расход создаются только в своем фонде, с суммой, pay_type и описанием. | [x] `app/services.py:create_transaction,_transaction_data; app/web.py:transaction_new`. | [x] `test_api.py:test_income_expense_and_integer_balances; test_foreign_fund_create_and_edit_are_forbidden`. Критерий: Разрешенные операции меняют верный баланс; подмена fund_id возвращает отказ и не изменяет БД. |
| ADM-03 | PDF 5, 8–9 | [x] Перевод разрешен только при Rights одновременно на from_fund_id и to_fund_id. | [x] `app/services.py:create_transfer,_transaction_data; app/web.py:transfer_new`. | [x] `test_integrity.py:test_transfer_requires_both_rights; test_auth_rbac.py:test_html_transfer_accepts_optional_empty_payment_type`. Критерий: Обе стороны доступны → успех; отсутствует одно/оба права → 403 и ноль записей перевода. |
| ADM-04 | PDF 2, 6, 9 | [x] Полная история своих фондов с фильтрами даты, типа операции и pay_type. | [x] `app/services.py:list_transactions,parse_filters; app/web.py:transactions`. | [x] `test_api.py:test_filters_include_whole_dates_and_combine; test_fund_and_transaction_lists_are_scoped`. Критерий: Фильтры работают по отдельности и вместе; фильтр чужого фонда не расширяет доступ. |
| ADM-05 | PDF 6, 9 | [x] Изменение/удаление разрешено только в своих фондах для собственных транзакций и транзакций Cashier. | [x] `app/services.py:_require_modify,edit_transaction,delete_transaction`. | [x] `test_api.py:test_admin_edit_delete_author_rule; test_integrity.py:test_transfer_edit_checks_old_and_new_funds`. Критерий: Своя/Cashier запись доступна; запись другого Admin/Super Admin запрещена; отзыв права блокирует изменение. |
| ADM-06 | PDF 2, 8–9 | [x] Admin не управляет пользователями, фондами, Rights и токенами и не получает Global Dashboard. | [x] `app/api.py:roles; app/auth.py:roles_required; app/web.py:dashboard/export/users/fund_form/rights/tokens`. | [x] `test_api.py:test_super_admin_api_role_matrix; test_auth_rbac.py:test_non_super_admin_cannot_open_management; test_global_dashboard_and_exports_role_enforcement`. Критерий: Прямые HTTP и соответствующие API вызовы возвращают 403. |

## 5. Cashier

| ID | Источник | Требование | Реализация | Проверка / критерий приемки |
|---|---|---|---|---|
| CASH-01 | PDF 6 | [x] Главный экран — большая простая форма: сумма, pay_type Наличные/Kaspi/Карта, комментарий, доступный фонд, «Принять оплату». | [x] `app/web.py:cashier; app/templates/cashier.html`. | [x] `test_auth_rbac.py:test_cashier_income_expense_history_and_no_transfer; browser/mobile gate дополнительно UI-01`. Критерий: Форма удобна на узком экране и создает income в доступном фонде. |
| CASH-02 | PDF 2, 6 | [x] Cashier видит только фонды из Rights и полную историю доходов/расходов этих фондов; чужие записи только read-only. | [x] `app/services.py:allowed_fund_ids,list_transactions; app/web.py:transactions`. | [x] `test_auth_rbac.py:test_html_foreign_fund_idor; test_cashier_cancels_only_last_own_transaction; test_cashier_shift_is_day_worked_and_contains_other_authors`. Критерий: Свои фонды видны, чужие скрыты/запрещены; чужие транзакции нельзя править/удалять. |
| CASH-03 | PDF 6 | [x] История смен: смена — день, когда работал кассир; это история по дням, без новых сущностей смен. | [x] `app/web.py:shifts; app/templates/shifts.html`. | [x] `test_auth_rbac.py:test_cashier_shift_is_day_worked_and_contains_other_authors`. Критерий: Дневная история показывает правильный период и данные доступных фондов. |
| CASH-04 | PDF 6 | [x] Можно отменить только свою последнюю ошибочную транзакцию либо пометить ее для проверки Admin. | [x] `app/services.py:cancel_last,last_cashier_transaction_id; app/web.py:transaction_cancel`. | [x] `test_auth_rbac.py:test_cashier_cancels_only_last_own_transaction; test_cashier_cannot_cancel_last_after_right_is_revoked; test_last_own_is_not_last_in_current_fund_filter`. Критерий: Последняя своя отменяется с пересчетом; более старая, чужая и недоступная запрещены. |
| CASH-05 | PDF 6 | [x] Форма изъятия наличных на нужды компании создает expense. | [x] `app/services.py:create_transaction; app/web.py:transaction_new; app/templates/transaction_form.html`. | [x] `test_auth_rbac.py:test_cashier_income_expense_history_and_no_transfer`. Критерий: Расход доступного фонда создает expense; сумма/способ движения сохранены. |
| CASH-06 | PDF 6 | [x] Cashier не видит чужие фонды и не выполняет межфондовые переводы/административные действия. | [x] `app/auth.py:roles_required; app/services.py:require_role,require_fund`. | [x] `test_auth_rbac.py:test_cashier_income_expense_history_and_no_transfer; test_non_super_admin_cannot_open_management; test_html_foreign_fund_idor`. Критерий: Прямой запрос transfer и административных форм запрещен; состояние денег не изменяется. |

## 6. Investor и глобальная отчетность

| ID | Источник | Требование | Реализация | Проверка / критерий приемки |
|---|---|---|---|---|
| INV-01 | PDF 2, 6–7 | [x] Investor строго read-only, в том числе при прямых запросах создания/изменения/удаления. | [x] `app/services.py:require_role; app/web.py:write route decorators`. | [x] `test_auth_rbac.py:test_investor_read_only_even_for_forged_post`. Критерий: Все финансовые и административные мутации запрещены. |
| INV-02 | PDF 2, 6–7 | [x] Главный экран Investor — Global Dashboard; он доступен только Investor/Super Admin. | [x] `app/web.py:index,dashboard; app/services.py:dashboard`. | [x] `test_auth_rbac.py:test_login_role_landing_and_logout; test_global_dashboard_and_exports_role_enforcement`. Критерий: Обе роли видят dashboard, Admin/Cashier получают 403. |
| INV-03 | PDF 2, 7 | [x] Детальная история доступных фондов только для просмотра; no_stats Investor не видит. | [x] `app/services.py:allowed_fund_ids,require_fund,list_transactions`. | [x] `test_auth_rbac.py:test_investor_details_require_rights_and_exclude_no_stats`. Критерий: Нет доступа к no_stats даже при Rights; прямой detail без Rights запрещен; разрешенный detail read-only. |
| DASH-01 | PDF 6–7 | [x] В глобальной статистике только for_stats; no_stats полностью исключены. | [x] `app/services.py:dashboard,allowed_fund_ids(global_view=True),export_rows`. | [x] `test_reporting.py:test_dashboard_kpis_and_balances_exclude_internal_flows; test_report_scope_includes_all_stats_but_redacts_hidden_counterpart`. Критерий: Большие тестовые суммы no_stats не меняют ни один KPI, ряд графика, таблицу или ленту. |
| DASH-02 | PDF 7 | [x] Общий баланс — сумма текущих остатков всех for_stats. | [x] `app/services.py:dashboard,ledger`. | [x] `test_reporting.py:test_dashboard_kpis_and_balances_exclude_internal_flows; test_dashboard_period_filters_flows_not_current_balance; test_integrity.py:test_archiving_preserves_history_balances_and_global_stats`. Критерий: Проверка вручную вычисленного баланса, включая переводы и архивные финансовые данные. |
| DASH-03 | PDF 7–8 | [x] Общий оборот — сумма внешних income за выбранный период; расходы — expense; чистый поток = оборот − расходы. | [x] `app/services.py:dashboard,parse_filters`. | [x] `test_reporting.py:test_dashboard_kpis_and_balances_exclude_internal_flows; test_api.py:test_filters_include_whole_dates_and_combine`. Критерий: Начало/конец периода включены корректно; inter-transaction не увеличивает оборот/расход/поток. |
| DASH-04 | PDF 6 | [x] Показаны доход за месяц, расход за месяц и чистая прибыль. | [x] `app/services.py:dashboard (month_income/month_expense/profit)`. | [x] `test_reporting.py:test_month_kpis_are_independent_from_chosen_period`. Критерий: Месяц рассчитывается отдельно от произвольного выбранного периода; нет придуманных налогов/начислений. |
| DASH-05 | PDF 6–7 | [x] График динамики поступлений и Donut/Pie распределения денег по фондам. | [x] `app/web.py:dashboard; app/templates/dashboard.html; app/services.py:dashboard (trend/distribution)`. | [x] `test_reporting.py` + визуальная проверка графика и распределения в desktop/mobile; см. `docs/VERIFICATION.md`. |
| DASH-06 | PDF 7 | [x] Таблица: название фонда, баланс, доход за период, расход за период. | [x] `app/templates/dashboard.html; app/services.py:dashboard (funds)`. | [x] `test_reporting.py:test_dashboard_kpis_and_balances_exclude_internal_flows; test_auth_rbac.py:test_investor_details_require_rights_and_exclude_no_stats`. Критерий: Все колонки заполнены правильными числами; нет no_stats; действия Investor только чтение. |
| DASH-07 | PDF 7–8 | [x] Хронологическая лента последних операций for_stats; внутренние переводы выделены специальным значком/меткой. | [x] `app/services.py:list_transactions,dashboard; app/templates/components/transactions_table.html`. | [x] `test_reporting.py:test_dashboard_kpis_and_balances_exclude_internal_flows; test_report_scope_includes_all_stats_but_redacts_hidden_counterpart; transfer icon/label проверены в шаблоне`. Критерий: Сортировка верна; межфондовое движение отличимо от внешнего; скрытый фонд не раскрывается через counterpart. |
| REPORT-01 | PDF 7 | [x] Выгрузка всех for_stats за выбранный период в CSV. | [x] `app/services.py:export_file(format=csv),export_rows; app/web.py:export`. | [x] `test_reporting.py:test_csv_and_real_excel_export_match; test_export_date_boundaries_and_invalid_requests; test_untrusted_text_is_not_a_csv_or_excel_formula`. Критерий: Проверены строки, заголовки, даты, денежные значения, отсутствие no_stats и скрытого counterpart. |
| REPORT-02 | PDF 7 | [x] Выгрузка всех for_stats за выбранный период в Excel. | [x] `app/services.py:export_file(format=xlsx); app/web.py:export`. | [x] `test_reporting.py:test_csv_and_real_excel_export_match; test_excel_preserves_minor_unit_integer_beyond_15_digits`. Критерий: XLSX открывается библиотекой Excel; данные соответствуют CSV/периоду, no_stats отсутствуют. |

## 7. Финансовые операции и токены

| ID | Источник | Требование | Реализация | Проверка / критерий приемки |
|---|---|---|---|---|
| FIN-01 | PDF 1–2, 4 | [x] Income повышает баланс фонда, expense снижает; pay_type обязателен для обоих. | [x] `app/services.py:create_transaction,_transaction_data,ledger`. | [x] `test_api.py:test_income_expense_and_integer_balances; test_required_pay_type_and_transaction_enum`. Критерий: При income 10000 и expense 2500 баланс 7500; отсутствующий pay_type отклонен. |
| FIN-02 | PDF 2, 4, 6 | [x] pay_type хранится строкой; поддерживаются Наличные, Kaspi, Карта и другие предусмотренные свободным строковым полем способы. | [x] `app/services.py:_transaction_data; app/templates/cashier.html and transaction_form.html`. | [x] `test_api.py:test_free_text_pay_type_and_negative_balance_are_supported; test_auth_rbac.py:test_cashier_income_expense_history_and_no_transfer`. Критерий: Предложенные способы работают; API не ограничен необоснованным enum из трех значений. |
| FIN-03 | PDF 8 | [x] Перевод создает ровно две связанные записи в одной DB-транзакции, обе хранят from/to; балансы обоих фондов обновляются сразу. | [x] `app/services.py:create_transfer,ledger; app/db.py:atomic,SCHEMA`. | [x] `test_integrity.py:test_transfer_has_two_rows_and_one_logical_history_entry`. Критерий: В БД две строки, общий transfer_id; X уменьшается ровно на money, Y увеличивается ровно на money; сумма остатков сохраняется. |
| FIN-04 | PDF 8; Цель §20–21 | [x] Ошибка между списанием и зачислением приводит к полному ROLLBACK. | [x] `app/db.py:atomic; app/services.py:write_operation,create_transfer`. | [x] `test_integrity.py:test_transfer_creation_rolls_back_when_credit_insert_fails`. Критерий: Инъекция ошибки во вторую запись оставляет обе таблицы/балансы в исходном состоянии. |
| FIN-05 | PDF 5, 8–9; Цель §20 | [x] Изменение/удаление финансовой операции сразу корректирует остатки; перевод остается согласованной парой. | [x] `app/services.py:edit_transaction,delete_transaction; app/db.py:atomic`. | [x] `test_integrity.py:test_pair_mutation_rolls_back_if_one_side_fails; test_edit_and_delete_through_credit_id_keep_pair_consistent; test_super_admin_can_move_transfer_endpoints_atomically; test_income_edit_to_expense_or_other_owned_fund_reconciles_balances`. Критерий: Изменение суммы/сторон и удаление через любой ID пары не оставляет одинокую вторую запись и пересчитывает все затронутые фонды. |
| FIN-06 | PDF 7–8 | [x] Межфондовые движения никогда не учитываются как внешний доход/расход компании. | [x] `app/services.py:dashboard (type-based external flows)`. | [x] `test_reporting.py:test_dashboard_kpis_and_balances_exclude_internal_flows`. Критерий: Переводы for_stats↔for_stats и for_stats↔no_stats не меняют внешний оборот/расход/поток. |
| TOKEN-01 | PDF 1, 5; Цель §13 | [x] Токен генерируется криптографически безопасно, имеет ровно 128 символов и показывается только один раз. | [x] `app/services.py:create_token; app/web.py:tokens; app/templates/tokens.html`. | [x] `test_management.py:test_token_generated_once_hash_only_and_revocation; test_token_uniqueness_and_blocked_owner`. Критерий: Длина/неповторяемость; повторное открытие списка/страницы не показывает секрет. |
| TOKEN-02 | PDF 3–5; Цель §13 | [x] Хранится только SHA-256-хэш токена; Authorization: Bearer token хэшируется для поиска владельца. | [x] `app/services.py:create_token; app/auth.py:authenticate_api`. | [x] `test_management.py:test_token_generated_once_hash_only_and_revocation; test_api.py:test_api_rejects_missing_or_invalid_token`. Критерий: Верный токен действует от владельца; неверный/отсутствующий возвращает 401 без утечки. |
| TOKEN-03 | PDF 5, 9; Цель §13, 19 | [x] Для каждого API-запроса проверяются активность токена/пользователя, срок 30 дней, актуальные role и Rights; сброс пароля отзывает токены владельца. | [x] `app/auth.py:authenticate_api; app/services.py:create_token,reset_password,revoke_token,block_user,allowed_fund_ids`. | [x] `test_auth_rbac.py:test_blocked_user_invalidates_login_session_and_api,test_session_and_api_permissions_refresh_after_role_change; test_management.py:test_grant_revoke_right_changes_existing_token_immediately,test_password_reset_revokes_existing_api_tokens,test_expired_api_token_is_rejected`. Критерий: просроченный/отозванный токен и токен заблокированного пользователя не работают; смена роли/отзыв Rights применяются сразу. |

## 8. Полная матрица API из PDF

**Всего 16 пар method/path.** `SA` = Super Admin, `A` = Admin. Cashier и Investor не перечислены в API-разделе PDF и получают **403** на все перечисленные методы/пути после успешной аутентификации. Их явно заданные интерфейсные возможности реализуются HTML routes. Неаутентифицированный/невалидный/отозванный токен дает **401**, а не 403. Никакие дополнительные API endpoints не требуются текстом страниц 1–10; генерация токенов, редактирование фонда и сброс пароля обязательно доступны в UI.

| ID | Источник | Требование: method/path и разрешенные роли | Реализация | Проверка / критерий приемки |
|---|---|---|---|---|
| API-01 | PDF 8 | [x] POST `/api/create_user` — SA; создание любой из четырех ролей. | [x] `app/api.py:create_user`. | [x] `test_management.py:test_create_users_all_roles_and_no_password_leak; test_api.py:test_super_admin_api_role_matrix`. Критерий: Успех SA; A/Cashier/Investor → 403; проверка полей/роли. |
| API-02 | PDF 8 | [x] PUT `/api/users/{id}/edit_user` — SA; редактирование данных, включая роль. | [x] `app/api.py:edit_user`. | [x] `test_management.py:test_user_edit_search_filter_password_reset_and_invalidation; test_api.py:test_super_admin_api_role_matrix`. Критерий: Изменения сохранены; остальные роли → 403. |
| API-03 | PDF 8 | [x] PATCH `/api/users/{id}/block` — SA; блокировка/разблокировка is_active. | [x] `app/api.py:block_user`. | [x] `test_auth_rbac.py:test_blocked_user_invalidates_login_session_and_api; test_api.py:test_super_admin_api_role_matrix`. Критерий: Оба направления работают; заблокированный пользователь/токен не авторизуется. |
| API-04 | PDF 8 | [x] POST `/api/create_fund` — SA. | [x] `app/api.py:create_fund`. | [x] `test_management.py:test_create_edit_archive_fund_and_metadata; test_api.py:test_super_admin_api_role_matrix`. Критерий: Фонд создан со всеми полями; остальные роли → 403. |
| API-05 | PDF 8 | [x] PATCH `/api/funds/{id}/archive` — SA; is_active=False, без удаления истории. | [x] `app/api.py:archive_fund`. | [x] `test_integrity.py:test_archiving_preserves_history_balances_and_global_stats; test_api.py:test_super_admin_api_role_matrix`. Критерий: Фонд архивирован; транзакции/остатки не потеряны; остальные роли → 403. |
| API-06 | PDF 8 | [x] POST `/api/rights` — SA; JSON user_id/fund_id. | [x] `app/api.py:grant_right`. | [x] `test_management.py:test_grant_revoke_right_changes_existing_token_immediately; test_api.py:test_super_admin_api_role_matrix`. Критерий: Право создано; несуществующие IDs отклонены; остальные роли → 403. |
| API-07 | PDF 9 | [x] DELETE `/api/rights/{user_id}/{fund_id}` — SA. | [x] `app/api.py:revoke_right`. | [x] `test_management.py:test_grant_revoke_right_changes_existing_token_immediately; test_api.py:test_super_admin_api_role_matrix`. Критерий: Право отозвано немедленно; остальные роли → 403. |
| API-08 | PDF 9 | [x] DELETE `/api/tokens/{id}` — SA; деактивация токена. | [x] `app/api.py:revoke_token`. | [x] `test_management.py:test_token_generated_once_hash_only_and_revocation; test_api.py:test_super_admin_api_role_matrix`. Критерий: Токен больше не работает; сохранена запись; остальные роли → 403. |
| API-09 | PDF 9 | [x] PUT `/api/transactions/{id}` — SA; глобальное редактирование. | [x] `app/api.py:global_edit`. | [x] `test_api.py:test_global_edit_delete_all_authors; test_super_admin_api_role_matrix; test_integrity.py:test_super_admin_can_move_transfer_endpoints_atomically`. Критерий: Корректируются любые записи, включая пару перевода; остальные роли → 403. |
| API-10 | PDF 9 | [x] DELETE `/api/transactions/{id}` — SA; глобальное удаление с пересчетом. | [x] `app/api.py:global_delete`. | [x] `test_api.py:test_global_edit_delete_all_authors; test_super_admin_api_role_matrix`. Критерий: Баланс соответствует оставшимся данным; остальные роли → 403. |
| API-11 | PDF 9 | [x] GET `/api/funds` — SA/A; Admin видит только свои Rights-фонды. | [x] `app/api.py:funds`. | [x] `test_api.py:test_fund_and_transaction_lists_are_scoped; test_admin_api_does_not_inherit_cashier_or_investor_ui_rights`. Критерий: A получает только назначенные фонды; Cashier/Investor → 403. |
| API-12 | PDF 9 | [x] POST `/api/transactions/add` — SA/A; income/expense, fund_id в Rights Admin. | [x] `app/api.py:add`. | [x] `test_api.py:test_income_expense_and_integer_balances; test_foreign_fund_create_and_edit_are_forbidden; test_invalid_money_cannot_create_or_edit`. Критерий: Свой фонд → успех; чужой → 403; недопустимый тип/сумма/pay_type отклонены. |
| API-13 | PDF 9 | [x] POST `/api/transactions/add_transfer` — SA/A; Rights Admin на обе стороны. | [x] `app/api.py:transfer`. | [x] `test_integrity.py:test_transfer_requires_both_rights; test_transfer_has_two_rows_and_one_logical_history_entry; test_api.py:test_admin_api_does_not_inherit_cashier_or_investor_ui_rights`. Критерий: Пара атомарна; отсутствие хотя бы одного права → 403; Cashier/Investor → 403. |
| API-14 | PDF 9 | [x] GET `/api/transactions` — SA/A; история своих фондов, фильтры date/pay_type. | [x] `app/api.py:transactions`. | [x] `test_api.py:test_fund_and_transaction_lists_are_scoped; test_filters_include_whole_dates_and_combine`. Критерий: Нет чужих записей; фильтры не обходят доступ; Cashier/Investor → 403. |
| API-15 | PDF 9 | [x] PUT `/api/transactions/{id}/edit` — SA/A; у Admin свой фонд и автор сам/Cashier. | [x] `app/api.py:edit`. | [x] `test_api.py:test_admin_edit_delete_author_rule; test_foreign_fund_create_and_edit_are_forbidden`. Критерий: Своя/Cashier запись → успех; другой Admin/SA/чужой фонд → 403. |
| API-16 | PDF 9 | [x] DELETE `/api/transactions/{id}/delete` — SA/A; те же ограничения. | [x] `app/api.py:delete`. | [x] `test_api.py:test_admin_edit_delete_author_rule; test_integrity.py:test_edit_and_delete_through_credit_id_keep_pair_consistent`. Критерий: Разрешенное удаление корректирует баланс; неразрешенное → 403 без изменения данных. |

## 9. Интерфейс и поставка

| ID | Источник | Требование | Реализация | Проверка / критерий приемки |
|---|---|---|---|---|
| UI-01 | PDF 4–7; Цель §17 | [x] Чистый адаптивный role-aware UI на Flask/Jinja2/Bootstrap с повторно используемыми шаблонами, навигацией, карточками, таблицами, формами, alerts и badges. | [x] `app/templates/base.html, components/, role templates; app/static/css/app.css; app/web.py`. | [x] Ролевые HTTP-тесты; desktop/mobile 390×844 без переполнения; формы кассира/перевода и меню проверены в браузере; `docs/VERIFICATION.md`. |
| UI-02 | Цель §25 | [x] Все кнопки/формы/ссылки выполняют заявленное действие; нет фиктивных endpoints, заглушек, незавершенных страниц. | [x] `app/web.py и app/auth.py: HTML routes; app/templates/`. | [x] 210 автоматических проверок, компиляция 19 шаблонов, браузерные вход/выход/навигация/прием оплаты/Excel/403/self-lockout/активные сессии; `docs/VERIFICATION.md`. |
| DONE-01 | Цель §21–23 | [x] Приложение запускается, SQLite создается, все четыре роли и финансовые сценарии работают. | [x] `app/__init__.py:create_app/init-db/create-superadmin; run.py; SQLite app/db.py`. | [x] Новая SQLite, CLI init-db/create-superadmin, реальный login/dashboard; Waitress запущен; обе базы прошли integrity/FK проверки; `docs/VERIFICATION.md`. |
| DONE-02 | Цель §21 | [x] Автотесты покрывают login/logout/blocked user, роли/Rights/403, операции/атомарность, API auth/tokens, server-side sessions, stats/dashboard, edit/delete/archive, CSV/Excel. | [x] `tests/conftest.py; tests/test_api.py; tests/test_auth_rbac.py; tests/test_integrity.py; tests/test_reporting.py; tests/test_management.py; tests/test_mobile.py; tests/test_sessions.py; tests/test_config.py`. | [x] Свежий полный запуск PDF-ТЗ-аудита: **222 passed in 96.18s**; focused auth/session: **68 passed**, management/integrity: **44 passed**, limiter-focused auth: **60 passed**, config: **5 passed**; включены QR, LAN URL, self-lockout, session revoke/expiry, login throttling и регрессионные проверки. |
| DONE-03 | Цель §22, 25 | [x] Повторная сверка готового кода с исходным PDF и независимый read-only аудит отдельным субагентом. | [x] Финальное сопоставление требование → код → тест. | [x] Повторно открыт полный исходный PDF; шесть специализированных security-проверок выполнены, подтвержденные дефекты исправлены; `docs/VERIFICATION.md`, `SECURITY_REPORT.md`. |

## Доказательства приемки

2026-10-08: свежая автоматическая приемка в `.venv` при повторной сверке PDF-ТЗ — **222 passed in 96.18s**; focused security suites — **68 + 44 + 60 passed**, config — **5 passed**:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q --basetemp=tmp/pytest_full_security_final2
```

Тесты используют отдельную SQLite для каждого сценария и реальные Flask HTTP requests. HTML CSRF включен; логин проходит настоящую проверку PBKDF2. Атомарность подтверждена SQL-триггерами `RAISE(ABORT)` на второй вставке, обновлении и удалении пары — проверен реальный rollback, а не только вызов mock. CSV читается `csv`, XLSX — `openpyxl`; проверены формулы-инъекции и точное сохранение целых сумм длиннее 15 цифр.

После первоначальной приемки сценарий SQL/XSS усилен: вредоносный текст записывается через настоящий POST API вместо прямого seed SQL. Финальный набор дополнительно проверяет self-lockout, server-side session revoke/expiry, login throttling, API-token expiry/reset revocation и защитные HTTP-заголовки.

**Финальная приемка завершена.** DASH-05, UI-01, UI-02, DONE-01 и DONE-03 закрыты; актуальные результаты и точный объем браузерной проверки — в `docs/VERIFICATION.md`. Неразрешенных бизнес-требований сверх документированных решений D01–D12 не выявлено.

### Свежая сверка PDF-ТЗ (2026-10-08)

- Исходный PDF повторно прочитан полностью: 10 страниц.
- Реестр Flask содержит все 16 обязательных API method/path из страниц 8–9: 10 Super Admin и 6 Admin; лишних заменяющих endpoint-ов в этой матрице нет.
- Полный регрессионный запуск: **222 passed in 96.18s**.
- `instance/demo.sqlite3`: `PRAGMA integrity_check = ok`, `PRAGMA foreign_key_check` не вернул нарушений; данные не очищались.
- Проверка схемы и текущей демо-базы подтверждает таблицы Users/Rights/Funds/Transactions/ApiTokens и серверные WebSessions/LoginAttempts; временные строки лимитера не являются бизнес-данными ТЗ.
- Все строки этой матрицы имеют три независимых статуса: извлечение требования, реализация и успешная проверка. Незакрытые только инфраструктурные security-проверки `pip-audit`/Semgrep отмечены в `SECURITY_CHECKLIST.md` и не являются пунктами PDF-ТЗ.

---

<a id="security-checklistmd"></a>
## Раздел 3: `SECURITY_CHECKLIST.md`

Исходный файл: [`SECURITY_CHECKLIST.md`](../SECURITY_CHECKLIST.md)

# Контрольный список безопасности

- [x] Проверена аутентификация
- [x] Проверена авторизация
- [x] Проверено повышение роли
- [x] Проверен IDOR
- [x] Проверена SQL-инъекция
- [x] Проверен XSS
- [x] Проверен CSRF
- [x] Проверен SSTI
- [x] Проверен SSRF
- [x] Проверен обход пути
- [x] Проверены загрузки файлов — поверхности загрузки нет
- [x] Проверены сессии
- [x] Проверены cookie
- [x] Проверены секреты
- [x] Проверены зависимости
- [x] Проверена конфигурация Flask
- [x] Проверены HTTP-заголовки
- [x] Bandit проверен — полный запуск дошёл до ошибки форматирования на тестовом Unicode-суррогате; production-проверка оставила только намеренную LAN-привязку `0.0.0.0`
- [ ] pip-audit завершён — запуск выполнен, но доступ к `pypi.org` завершился `WinError 10013`; advisory-результат недоступен
- [ ] Semgrep завершён — загрузка конфигурации правил не удалась на этом хосте; валидного отчёта нет
- [x] Codex Security Deep Scan завершён — канонический запечатанный результат содержит 13 находок, сверенных с `SECURITY_REPORT.md`
- [x] Повторный Standard Scan текущего дерева завершён — скан `8bf38005-df71-4df8-8fd3-ff554bc45847` запечатан с 3 описанными находками
- [x] OWASP ZAP проверен, где возможно — локально недоступен; выполнена безопасная базовая проверка localhost
- [x] Ограничение входа проверено — известные и неизвестные логины используют одну корзину и получают одинаковый ответ лимита
- [x] Хранилище попыток входа ограничено — заблокированный клиент не создаёт новые строки; предел и очистка покрыты тестами
- [x] Общий бюджет входа проверен — смена адресов клиента не обходит нормализованный лимит логина
- [x] Изменение архивного журнала проверено — пути удаления/отмены Admin/Cashier требуют активный фонд
- [x] Проверка авторизации во время запроса проверена — операции записи перечитывают сессию/токен/пользователя внутри транзакции
- [x] Срок хранения истёкших/отозванных сессий проверен — очистка за 30 дней покрыта регрессионными тестами

## Ворота релиза

- [x] Подтверждённых Critical-уязвимостей нет
- [x] После исправлений подтверждённых High-уязвимостей нет
- [x] Medium-находки исправлены или описаны ограничениями deployment
- [x] Ложные срабатывания проверены вручную и зафиксированы
- [x] Существующие бизнес-потоки сохранены полным набором тестов
- [x] Super Admin видит и отзывает активные сессии
- [x] Браузерные сессии завершаются ровно через 24 часа
- [x] Logout отзывает доступ копии cookie
- [x] API-токены истекают и отзываются при сбросе пароля
- [x] Полный регрессионный набор проходит — 222 тест
- [x] Канонический отчёт Codex Security Deep приложен и сверен
- [x] Повторный Standard-отчёт текущего дерева приложен и сверен

---

<a id="security-reportmd"></a>
## Раздел 4: `SECURITY_REPORT.md`

Исходный файл: [`SECURITY_REPORT.md`](../SECURITY_REPORT.md)

# Отчёт аудита безопасности

Дата аудита: 2026-10-07  
Проект: Cybran Software (`Python / Flask / SQLite / Jinja2 / Bootstrap`)  
Охват: весь текущий репозиторий, локальный экземпляр `127.0.0.1:5000`  
Статус: исправления применены и проверены; канонические Codex Security Deep и повторный Standard scans запечатаны.

## 1. Резюме

Подтверждённых Critical или High уязвимостей после исправлений нет. Устранены повторное использование украденной cookie после выхода, отсутствие серверного управления сессиями, 31-дневный неявный срок browser-cookie, отсутствие ограничения попыток входа, timing/rate-limit oracle имени пользователя, общий lockout за reverse proxy, удаление истории архивного фонда нижними ролями, бессрочные API-токены, сохранение токена после сброса пароля, различимые ответы для чужих transaction ID, отсутствующая CSP и известные уязвимости зафиксированных версий Flask/pytest.

Super Admin теперь видит активные browser-сессии, IP, устройство, время входа, последней активности и автовыхода. Он может завершить выбранную сессию, все остальные либо абсолютно все. Каждая сессия имеет абсолютный срок 24 часа; активность не продлевает его. Logout отзывает запись на сервере, поэтому копия старой cookie больше не работает.

Остаётся **Medium deployment risk**: режим телефона намеренно публикует приложение в локальной сети по незашифрованному HTTP. Участник недоверенной Wi-Fi/LAN с возможностью перехвата трафика может получить пароль, cookie или Bearer-токен до их отзыва. В коде и терминале добавлено явное предупреждение; режим допускается только для доверенной изолированной сети. Для production обязателен HTTPS, `COOKIE_SECURE=1` и TLS reverse proxy.

Простые пароли сохранены только для явно выбранной демонстрационной базы по прямому требованию владельца. Деморежим теперь заметно помечен на странице входа и в терминале. Использование demo DB с реальными данными или в недоверенной сети запрещено.

## 2. Использованные инструменты

- **Codex Security Deep Scan** — канонически завершён и запечатан; 13 findings на pre-fix snapshot.
- **Codex Security Standard Scan** — повторно выполнен по текущему дереву и запечатан; 3 findings (2 Medium, 1 Low).
- **Шесть специализированных subagent-проверок** — auth/authz, backend, frontend/Jinja, dependencies/config, dynamic testing, attack-path analysis.
- **Bandit 1.9.4** — production Python-код, 1 оставшееся предупреждение `B104` для осознанного LAN bind.
- **pip-audit 2.10.1** — запуск выполнен, но доступ к `pypi.org` заблокирован Windows sandbox (`WinError 10013`); итог базы уязвимостей не получен.
- **Semgrep 1.179.0** — запуск профилей Python/Flask/OWASP/secrets выполнен, но конфигурации не загрузились на этом хосте из-за certificate/network/config error; валидного нулевого отчёта нет.
- **OWASP ZAP** — CLI/API отсутствует на машине. Проверена доступность инструмента; вместо active scan выполнен безопасный localhost baseline без destructive testing.
- **pytest 9.0.3** — полный regression/security suite: `222 passed` после всех исправлений.
- Ручной source review, Jinja compile, SQLite integrity/foreign-key checks, browser visual QA и безопасные HTTP-пробы.

Полный требуемый `bandit -r .` был выполнен в JSON и текстовом форматах. Оба запуска дошли до форматирования результатов, но не смогли сериализовать намеренно некорректный Unicode-суррогат из regression-теста; это ограничение вывода инструмента, а не подтверждённая уязвимость. Повторный production scan `bandit -r app run.py` завершился одним осознанным `B104` для LAN bind в `run.py:11`; SQL `B608` отмечены как проверенные false positive: идентификаторы берутся только из фиксированных allowlist/tuple, значения параметризованы.

## 3. Поверхность атаки

Основные точки входа:

- публичная HTML-форма `/login`;
- подписанная browser-cookie плюс серверный `WebSessions` registry;
- Bearer authentication для `/api/*`;
- Super Admin management: пользователи, права, токены и browser-сессии;
- финансовые операции, переводы, фонды и экспорты CSV/XLSX;
- локальный Waitress listener и QR/LAN URL;
- SQLite-файлы и локальный `session.key` вне Git.

Прямой upload/download по пользовательскому пути, SSRF-клиент, shell/subprocess, pickle/deserialization и пользовательский выбор шаблона отсутствуют.

### Матрица авторизации маршрутов

`PASS` означает проверку прав на backend. `PASS/MITIGATED` означает, что найденный риск исправлен и покрыт regression-тестом.

| METHOD | ROUTE | AUTH | ROLE | OBJECT CHECK | STATUS |
|---|---|---|---|---|---|
| GET | `/` | Cookie + server session | Any active | Role landing | PASS |
| GET/POST | `/login` | Public; CSRF on POST | — | Rate limit by IP/account | PASS/MITIGATED |
| POST | `/logout` | Cookie + CSRF | Any active | Current server session | PASS/MITIGATED |
| GET | `/dashboard` | Cookie | Super Admin, Investor | Global `for_stats` per specification | PASS |
| GET | `/reports/export` | Cookie | Super Admin, Investor | `for_stats`, validated filters | PASS |
| GET | `/funds` | Cookie | All roles | `allowed_fund_ids()` | PASS |
| GET | `/funds/<fund_id>` | Cookie | All roles | `require_fund()` | PASS |
| GET/POST | `/funds/new` | Cookie + CSRF | Super Admin | Fixed fields | PASS |
| GET/POST | `/funds/<fund_id>/edit` | Cookie + CSRF | Super Admin | Existing fund | PASS |
| POST | `/funds/<fund_id>/archive` | Cookie + CSRF | Super Admin | Existing fund | PASS |
| GET | `/transactions` | Cookie | All roles | Rights + counterpart redaction | PASS |
| GET/POST | `/transactions/new` | Cookie + CSRF | Super Admin, Admin, Cashier | Fund Rights | PASS |
| GET/POST | `/transfers/new` | Cookie + CSRF | Super Admin, Admin | Rights on both funds | PASS |
| GET/POST | `/transactions/<id>/edit` | Cookie + CSRF | Super Admin, Admin | Rights + author policy; hidden 404 | PASS/MITIGATED |
| POST | `/transactions/<id>/delete` | Cookie + CSRF | Super Admin, Admin | Rights + author policy; hidden 404 | PASS/MITIGATED |
| GET/POST | `/cashier` | Cookie + CSRF | Super Admin, Cashier | Rights; type forced server-side | PASS |
| GET | `/shifts` | Cookie | Super Admin, Cashier | Accessible funds/own work days | PASS |
| POST | `/transactions/<id>/cancel` | Cookie + CSRF | Super Admin, Cashier | Own latest ordinary transaction; hidden 404 | PASS/MITIGATED |
| GET | `/users` | Cookie | Super Admin | — | PASS |
| GET/POST | `/users/new` | Cookie + CSRF | Super Admin | Field allowlist | PASS |
| GET/POST | `/users/<id>/edit` | Cookie + CSRF | Super Admin | Self/last-SA invariant | PASS |
| POST | `/users/<id>/block` | Cookie + CSRF | Super Admin | Self/last-SA invariant | PASS |
| POST | `/users/<id>/password` | Cookie + CSRF | Super Admin | Existing user; sessions/tokens invalidated | PASS/MITIGATED |
| GET/POST | `/rights` | Cookie + CSRF | Super Admin | User/fund existence; atomic replace | PASS |
| GET/POST | `/tokens` | Cookie + CSRF | Super Admin | Active owner; 30-day expiry | PASS/MITIGATED |
| POST | `/tokens/<id>/revoke` | Cookie + CSRF | Super Admin | Existing token | PASS |
| GET | `/sessions` | Cookie | Super Admin | Only valid active sessions | PASS/NEW |
| POST | `/sessions/<id>/revoke` | Cookie + CSRF | Super Admin | Existing active session | PASS/NEW |
| POST | `/sessions/revoke-all` | Cookie + CSRF | Super Admin | Current/all scope is server-controlled | PASS/NEW |
| POST | `/api/create_user` | Bearer | Super Admin | Fixed fields | PASS |
| PUT | `/api/users/<id>/edit_user` | Bearer | Super Admin | Self/last-SA invariant | PASS |
| PATCH | `/api/users/<id>/block` | Bearer | Super Admin | Strict boolean + self/last-SA invariant | PASS |
| POST | `/api/create_fund` | Bearer | Super Admin | Fixed fields | PASS |
| PATCH | `/api/funds/<id>/archive` | Bearer | Super Admin | Existing fund | PASS |
| POST | `/api/rights` | Bearer | Super Admin | User/fund existence | PASS |
| DELETE | `/api/rights/<uid>/<fid>` | Bearer | Super Admin | Validated IDs | PASS |
| DELETE | `/api/tokens/<id>` | Bearer | Super Admin | Existing token | PASS |
| PUT/DELETE | `/api/transactions/<id>` | Bearer | Super Admin | Existing transaction | PASS |
| GET | `/api/funds` | Bearer | Super Admin, Admin | Admin Rights | PASS |
| POST | `/api/transactions/add` | Bearer | Super Admin, Admin | Fund Rights | PASS |
| POST | `/api/transactions/add_transfer` | Bearer | Super Admin, Admin | Rights on both funds | PASS |
| GET | `/api/transactions` | Bearer | Super Admin, Admin | Rights + redaction | PASS |
| PUT | `/api/transactions/<id>/edit` | Bearer | Super Admin, Admin | Rights + author policy; hidden 404 | PASS/MITIGATED |
| DELETE | `/api/transactions/<id>/delete` | Bearer | Super Admin, Admin | Rights + author policy; hidden 404 | PASS/MITIGATED |
| GET | `/static/<path>` | Public | — | Flask static root | PASS |

В проекте нет ролей Student/Staff. Их эквивалентные негативные сценарии проверены как Cashier/Investor → Admin/Super Admin, Admin → Super Admin, user/fund A → object B.

## 4. Аутентификация и авторизация

- Login очищает прежнюю cookie, создаёт криптографически случайный server session token и хранит в SQLite только SHA-256 hash.
- Browser-сессия проверяет: пользователя, `is_active`, `auth_version`, server-side revoke state и абсолютный `expires_at`.
- Logout атомарно отзывает текущую запись до очистки cookie.
- Абсолютный срок browser-сессии — 24 часа; Flask-cookie также permanent с 24-часовым сроком без sliding refresh.
- Super Admin имеет отдельную страницу управления активными сессиями.
- Login имеет 5 попыток на пару IP/account и 30 на IP за 5 минут, ответ `429` + `Retry-After`.
- За HTTPS reverse proxy приложение принимает client IP только при явно заданном `TRUSTED_PROXY_HOPS`; backend должен быть закрыт от обхода proxy.
- Неизвестный/заблокированный пользователь проходит dummy PBKDF2 path; текст ошибки одинаковый.
- API token случайный, хранится hash-only, показывается один раз, действует 30 дней и отзывается при password reset.
- CSRF обязателен для browser mutations; API не использует ambient cookie и требует Bearer.
- Role и object checks выполняются в service layer, поэтому прямой endpoint-вызов не обходит UI.
- Self-block, self-downgrade и удаление последнего активного Super Admin запрещены внутри `BEGIN IMMEDIATE`.

## 5. Уязвимости

### CYB-SEC-001 — Незашифрованный транспорт в LAN

- **Severity:** Medium (remaining, deployment-dependent)
- **CWE:** CWE-319, CWE-614
- **OWASP:** A02:2021 Cryptographic Failures
- **File:** `run.py:11`, `app/__init__.py:20`
- **Vulnerable behavior:** default phone mode binds `0.0.0.0` and advertises `http://`; `Secure` cookie is opt-in.
- **Reason:** HTTP does not protect credentials, cookie or Bearer token in transit.
- **Attack scenario:** attacker on a malicious/shared Wi-Fi captures a live credential and replays it before expiry/revocation.
- **Required rights:** network position in the same LAN/AP; no application account required.
- **Impact:** victim-account takeover; Super Admin compromise reaches the full management surface.
- **Fix:** TLS reverse proxy/tunnel, trusted certificate, `COOKIE_SECURE=1`; do not send Bearer over HTTP.
- **Status:** **Documented remaining risk.** Terminal warning and README restriction added. Accepted only for isolated trusted LAN/mobile demo.

### CYB-SEC-002 — Logout не отзывал скопированную cookie

- **Severity:** Medium; part of the initial High chain when combined with plaintext transport
- **CWE:** CWE-613
- **OWASP:** A07:2021 Identification and Authentication Failures
- **File:** formerly `app/auth.py`; fixed in `app/auth.py:88-143,203-209`, `app/db.py:41-55`
- **Attack scenario:** stolen signed cookie remained usable after the victim clicked logout.
- **Fix:** server-side session registry, hashed session token, logout/admin revocation and 24-hour absolute expiry.
- **Status:** **Fixed.** Copied-cookie replay regression test passes.

### CYB-SEC-003 — Неограниченные попытки входа и временная oracle-утечка имени

- **Severity:** Medium
- **CWE:** CWE-307, CWE-208
- **OWASP:** A07:2021
- **File:** fixed in `app/auth.py:34-79,177-199`
- **Attack scenario:** online password guessing plus measurement of PBKDF2/no-PBKDF2 latency to enumerate valid active users.
- **Fix:** persistent bounded window rate limit, `429/Retry-After`, dummy PBKDF2 verification and stale-counter cleanup.
- **Status:** **Fixed.** Boundary and storage-growth tests pass.

### CYB-SEC-009 — Различие rate limit раскрывало существование имени

- **Severity:** Medium (fixed)
- **CWE:** CWE-204
- **OWASP:** A07:2021 Identification and Authentication Failures
- **File:** fixed in `app/auth.py:43-79,177-199`
- **Attack scenario:** known usernames previously shared a persistent account bucket while unknown names did not; comparing the sixth failed request could distinguish an existing account from a missing one even though the HTTP error text matched.
- **Fix:** derive the account bucket from a normalized username hash before lookup, while retaining the per-IP bucket; known and unknown names now receive the same 5-attempt limit and `429/Retry-After` behavior.
- **Status:** **Fixed.** Regression coverage verifies identical throttling for a real and a missing username; focused auth suite passes.

### CYB-SEC-010 — Адрес reverse proxy вызывал общий lockout входа

- **Severity:** Medium (fixed with explicit deployment configuration)
- **CWE:** CWE-400
- **OWASP:** A07:2021 Identification and Authentication Failures
- **File:** fixed in `app/__init__.py:10-41`, `app/auth.py:43-79`, `README.md:23`
- **Attack scenario:** when a documented HTTPS reverse proxy was used without restoring the original client address, every login shared the proxy's `request.remote_addr`; an unauthenticated client could exhaust the 30-attempt peer bucket and temporarily block new logins for other users.
- **Fix:** add `TRUSTED_PROXY_HOPS` and Werkzeug `ProxyFix` for the exact controlled hop count, so rate-limit keys use the real client address. Documentation requires the backend firewall boundary and forbids trusting forwarded headers from direct clients.
- **Status:** **Fixed in code; deployment gate documented.** Regression test verifies two forwarded client addresses receive independent login buckets. Edge rate limiting remains recommended.

### CYB-SEC-011 — Удаление архивного журнала нижними ролями

- **Severity:** Medium (fixed)
- **CWE:** CWE-862, CWE-639
- **OWASP:** A01:2021 Broken Access Control
- **File:** fixed in `app/services.py:124-132,329-347`
- **Attack scenario:** Admins with fund Rights could delete ordinary or paired transactions from archived funds; Cashiers could cancel their last ordinary archived transaction, changing protected history and balances.
- **Fix:** service-layer mutation checks now pass `writing=True` for Admin/Cashier fund access, while Super Admin retains the documented archived-history correction path. Both HTML and Bearer API routes use the same service guard.
- **Status:** **Fixed.** Regression tests cover Admin deletion and Cashier cancellation after archive; Super Admin correction tests remain green.

### CYB-SEC-012 — Строки попыток входа росли от новых имён

- **Severity:** Medium (fixed)
- **CWE:** CWE-400
- **OWASP:** A07:2021 Identification and Authentication Failures
- **File:** fixed in `app/auth.py:54-113`, `app/__init__.py:24-26`
- **Attack scenario:** a client could submit a new username after its IP bucket was already blocked; the old loop inserted the username key before deciding to return `429`, leaving persistent rows in SQLite.
- **Fix:** evaluate the peer bucket before allocating account-specific rows, purge expired rows, and enforce a hard maximum row count with oldest-row eviction. An account-wide bounded bucket also limits distributed guessing.
- **Status:** **Fixed.** Regression tests verify blocked clients do not allocate fresh rows and account throttling survives rotating proxy clients.

### CYB-SEC-013 — Бюджет подбора зависел от исходного адреса

- **Severity:** Medium (fixed)
- **CWE:** CWE-307
- **OWASP:** A07:2021 Identification and Authentication Failures
- **File:** fixed in `app/auth.py:43-50`, `app/__init__.py:24-26`
- **Attack scenario:** rotating source addresses could previously reset the account-plus-IP bucket and supply unbounded guesses against one account.
- **Fix:** add a normalized username account bucket with an address-independent limit, retain the per-account/IP and peer limits, and keep known/unknown response behavior equalized.
- **Status:** **Fixed.** A regression test rotates 21 forwarded client addresses and confirms the account budget returns `429`.

### CYB-SEC-014 — Отзыв мог пересечься с последующей записью

- **Severity:** Medium (fixed)
- **CWE:** CWE-613, CWE-367
- **OWASP:** A07:2021 Identification and Authentication Failures
- **File:** fixed in `app/services.py:21-61`
- **Attack scenario:** a request authenticated before a concurrent block, auth-version change, browser-session revoke, or API-token revoke could reach a later mutation using a stale user dictionary.
- **Fix:** every request-bound `write_operation` reloads the actor inside `BEGIN IMMEDIATE` and rechecks active state, auth version, browser session row, or API token row before dispatching the service function.
- **Status:** **Fixed.** Direct service tests and the full API/management suites pass.

### CYB-SEC-015 — Отозванные и истёкшие сессии не имели срока хранения

- **Severity:** Low (fixed)
- **CWE:** CWE-400
- **OWASP:** A05:2021 Security Misconfiguration
- **File:** fixed in `app/auth.py:167-185`, `app/__init__.py:20`
- **Attack scenario:** repeated login/logout cycles retained unusable `WebSessions` rows indefinitely, growing the SQLite file and backups.
- **Fix:** prune expired sessions and revoked sessions older than the configured 30-day audit retention during request processing; current expired-session behavior is preserved before pruning.
- **Status:** **Fixed.** Retention regression test passes.

### CYB-SEC-016 — Рост журнала не ограничивался квотой приложения

- **Severity:** Low (availability/operations)
- **CWE:** CWE-400
- **OWASP:** A05:2021 Security Misconfiguration
- **File:** `app/services.py:520-560` (ledger write paths)
- **Attack scenario:** an authenticated writer can continue creating valid transactions until the SQLite file, backups, or available disk space become the limiting resource. This is an operational capacity risk rather than an unauthorized-write path; role, fund Rights, validation and archived-fund checks still apply.
- **Fix/status:** **Documented residual risk.** Add deployment-level disk quotas, backup/retention monitoring and alerting before high-volume or internet-facing use. No safe destructive load test was run.

### CYB-SEC-004 — API-токен переживал восстановление после компрометации и не истекал

- **Severity:** Medium
- **CWE:** CWE-613
- **OWASP:** A07:2021
- **File:** fixed in `app/auth.py:158-170`, `app/services.py:421-425,494-505`, `app/db.py:32-40`
- **Attack scenario:** stolen Admin/Super Admin Bearer remained active after password reset indefinitely.
- **Fix:** 30-day absolute expiry; password reset revokes all owner tokens; expiry shown in UI.
- **Status:** **Fixed.** Expired/reset token tests pass.

### CYB-SEC-005 — Oracle существования транзакции

- **Severity:** Low
- **CWE:** CWE-203, CWE-639
- **OWASP:** A01:2021 Broken Access Control
- **File:** fixed in `app/services.py:282-294`
- **Attack scenario:** inaccessible existing ID returned 403 while missing ID returned 404.
- **Impact:** disclosed only the existence of an integer ID; no row contents or mutation.
- **Fix:** inaccessible and absent protected transactions both return 404.
- **Status:** **Fixed.** HTML/API regression tests pass.

### CYB-SEC-006 — Не хватало заголовков изоляции браузера

- **Severity:** Low
- **CWE:** CWE-693
- **OWASP:** A05:2021 Security Misconfiguration
- **File:** fixed in `app/__init__.py:89-102`
- **Attack scenario:** no standalone XSS was found; missing CSP could amplify a future escaping defect.
- **Fix:** CSP, Permissions-Policy and HTTPS-only HSTS.
- **Status:** **Fixed as hardening.** Jinja autoescape remains the primary XSS control.

### CYB-SEC-007 — Предсказуемые демо-реквизиты

- **Severity:** Medium only if demo DB is exposed outside an isolated test environment
- **CWE:** CWE-798
- **OWASP:** A07:2021
- **File:** `app/demo.py:16-20,50-52`
- **Reason:** simple source-known passwords are intentionally generated for manual testing.
- **Required rights:** network access to an intentionally seeded demo instance.
- **Fix:** production must use `create-superadmin`, a clean DB and unique strong credentials.
- **Status:** **Accepted demo-only risk.** Seed is explicit/empty-DB-only; instance is ignored; login and terminal show a prominent demo warning. Values are not reproduced in this report.

### CYB-SEC-008 — Уязвимые закреплённые версии зависимостей

- **Severity:** Low runtime + Medium dev/UNIX conditional
- **CVE:** CVE-2026-27205 (Flask 3.1.2), CVE-2025-71176 (pytest 8.4.2)
- **Files:** `requirements.txt`
- **Fix:** Flask 3.1.3; pytest 9.0.3; pip 26.2.1 in the audit environment.
- **Status:** **Pinned versions updated; automated advisory verification is pending.** `pip-audit` could not reach `pypi.org` in this environment, so no zero-vulnerability claim is made here.

## 6. Уязвимости зависимостей

| Package | Before | Advisory | Severity/context | Fixed version | Result |
|---|---:|---|---|---:|---|
| Flask | 3.1.2 | CVE-2026-27205 / GHSA-68rp-wp8r-4726 | Low; current no-store headers also blocked known cache preconditions | 3.1.3 | Updated |
| pytest | 8.4.2 | CVE-2025-71176 / GHSA-6w46-j5rx-g56g | Medium; UNIX local temp issue, dev-only on this Windows host | 9.0.3 | Updated |
| pip | 25.0.1 | tooling/archive advisories | Build/install environment only | 26.2.1 | Updated |

Current dependency evidence: `pip check` reports **No broken requirements found**. `pip-audit` was attempted with a short timeout but could not connect to `pypi.org` (`WinError 10013`), so advisory status remains unverified until CI or a network-enabled host runs it.

## 7. Статический анализ

### Bandit

- Production source LOC inspected: 1,400+.
- Final report: one Medium `B104`, `run.py:11`, intentional `0.0.0.0` LAN bind (CYB-SEC-001).
- SQL `B608` warnings manually validated and suppressed with exact rationale: table/columns are fixed allowlists/constants; all external values use SQLite placeholders.
- The extra `B104` comparison-only warning was suppressed; the actual bind remains visible.

### Semgrep

- Packs: Python, Flask, OWASP Top 10, secrets, SQL injection, command injection, insecure transport.
- The configured production profiles were attempted, but Semgrep could not load the remote/local rule packs on this host (certificate/config/network error) and produced no valid JSON findings report. This is an environmental limitation, not a clean scan result. All 19 current templates are compiled separately by Jinja.

### Ручная статическая проверка

- No `eval`, `exec`, shell execution, unsafe deserialization, upload sink, user-controlled file path or outbound HTTP client.
- No `|safe`, `Markup`, `render_template_string`, dynamic template name or dangerous DOM HTML sink.
- No real provider key/private key/token in the working tree or four available Git commits. Values from test/demo fixtures are classified separately and masked.

## 8. Динамический анализ

OWASP ZAP is not installed; no third-party target was scanned. Safe localhost checks covered:

- protected HTML routes redirect anonymous users to login;
- API routes reject missing/invalid Bearer with 401 and no traceback;
- modifying HTML routes reject missing/bad CSRF;
- SQLi/XSS/SSTI-like login values do not authenticate or reflect as executable HTML;
- foreign Origin receives no permissive CORS headers;
- `next=` does not create an open redirect;
- literal/encoded static traversal returns 404;
- TRACE is rejected and logout does not accept GET;
- arbitrary Host does not reach an absolute URL sink;
- security headers and cookie flags are present as designed;
- browser QA confirms the Super Admin session-management page and visible 24-hour policy.

No destructive testing, DoS, external IP/domain scan or database deletion was performed.

## 9. Пути атаки

1. **LAN HTTP → captured cookie/Bearer → privileged endpoint** — reportable Medium, remains until HTTPS. Server-side expiry/revocation limits duration but cannot encrypt transit.
2. **Published demo instance → known simple Super Admin password → control plane** — conditional Medium; accepted only in isolated demo scope, warning added.
3. **Reverse proxy peer → shared login limiter → temporary lockout** — mitigated by explicit trusted-hop client-IP restoration and backend isolation.
4. **Archived fund → lower-role delete/cancel → ledger history change** — mitigated by active-fund mutation checks in the service layer.
5. **Stolen cookie → victim logout → replay** — mitigated by `WebSessions.revoked_at` lookup.
6. **Weak online auth → username enumeration → password guessing** — mitigated by dummy PBKDF2 and equalized rate limiting.
7. **Stolen Bearer → password reset → continued API access** — mitigated by token revocation and expiry.
8. **Controlled object ID → IDOR/role escalation** — ignored after validation; backend Rights/role/author checks hold.
9. **Stored/reflected text → XSS → victim action** — ignored; no executable source-to-sink path. CSP added as containment.
10. **Host/next input → external redirect** — ignored; no external URL sink.

## 10. Применённые исправления

- Server-side hashed browser-session registry.
- Super Admin active-session page and single/bulk termination.
- Absolute 24-hour session lifetime and non-sliding cookie expiry.
- Logout revocation and replay prevention.
- Persistent bounded login throttling with stale-row cleanup.
- Dummy PBKDF2 verification for unknown users.
- Equalized account rate-limit buckets for known and unknown usernames.
- Explicit trusted-proxy client-IP restoration for rate limiting.
- Active-fund guard for Admin/Cashier transaction edits, deletes and cancellations.
- 30-day API-token expiry and reset-time revocation.
- Uniform 404 for inaccessible transaction IDs.
- CSP, Permissions-Policy and HTTPS-only HSTS.
- Demo-mode UI/terminal warnings.
- Flask, pytest and pip security updates.
- Focused regression coverage for every applied fix.

## 11. Остаточные риски

- **Medium:** plaintext HTTP on LAN/mobile. Treat the network as trusted or deploy TLS.
- **Medium conditional:** simple demo credentials if the demo DB is exposed. Never use demo mode with real data.
- **Deployment gate:** set `TRUSTED_PROXY_HOPS` only behind a controlled HTTPS proxy and block direct backend access; otherwise proxy-wide rate limiting is intentionally not considered safe.
- **Low hardening:** CSP temporarily allows inline style because existing charts use inline style attributes. No script inline/eval is allowed.
- **Low operational:** ledger volume and SQLite disk growth need deployment quotas, backup/retention monitoring and alerting. Expired/revoked web sessions and stale rate-limit rows are pruned automatically, but ledger history is intentionally retained.
- OWASP ZAP active/passive scanner evidence is unavailable on this host; safe localhost baseline is documented instead.
- Canonical Codex Security Deep Scan is sealed with 13 findings (8 Medium, 5 Low) against its earlier snapshot; fixed findings are reconciled below. The repeat current-tree Standard scan `8bf38005-df71-4df8-8fd3-ff554bc45847` is also sealed with 3 findings (2 Medium, 1 Low): the remaining HTTP LAN/demo deployment risks and low operational ledger-growth risk.

## 12. Усиление production-конфигурации

1. Put Waitress behind HTTPS reverse proxy; set `COOKIE_SECURE=1`; keep HSTS enabled only on HTTPS.
2. Bind loopback by default in production orchestration; explicitly expose only the intended interface/firewall subnet.
3. Use a clean non-demo SQLite database and unique strong passwords; remove `demo-access.txt` after testing.
4. Supply `SECRET_KEY` from a protected deployment secret and back up/rotate it under an incident procedure.
5. Configure a trusted Host allowlist at the reverse proxy/application boundary before internet exposure.
6. Move chart inline styles to nonce/hash-compatible CSS if a stricter CSP without `'unsafe-inline'` is required.
7. Add centralized audit logging/alerting for login throttles, session revocations and privileged changes.
8. Run Bandit, pip-audit, Semgrep and the complete test suite in CI on every dependency/code change.
9. Run OWASP ZAP baseline against a disposable HTTPS staging instance before release.

## 13. Финальная проверка

Current verified evidence:

- `pytest -q --basetemp=tmp\pytest_config_full`: **222 passed in 96.18s** after adding project `.env` and configurable payment-method settings; bounded limiter, TOCTOU and session-retention fixes remain green.
- Focused auth/session/control suites: **68 passed** for auth + sessions; **44 passed** for management + integrity; **60 passed** for auth limiter after bounded-budget fixes.
- Frontend-focused checks: **3 passed**.
- Bandit final: only intentional/reportable `B104` LAN bind.
- `pip-audit`: attempted but blocked by `pypi.org` network/permission (`WinError 10013`); no vulnerability result.
- Semgrep: attempted but configuration scan failed on this host; no valid findings result.
- Browser: active-session UI is role-restricted and exposes no session token/hash.
- Live app: one Waitress instance, demo migration applied, login/session registry operational.
- Codex Security Deep Scan: **complete and sealed**; 13 findings on the earlier snapshot, with current-tree fixes reconciled in this report.
- Repeat current-tree Standard scan: **complete and sealed**; 3 findings (2 Medium, 1 Low), all documented in this report.

This report contains no complete password, API token, cookie, session identifier or secret key.

---

<a id="docs-apimd"></a>
## Раздел 5: `docs/api.md`

Исходный файл: [`docs/api.md`](../docs/api.md)

# REST API

Все запросы API используют `Authorization: Bearer <128-символьный токен>`. Токен создаёт Super Admin на странице «API-токены», секрет показывается один раз и хранится в SQLite только как SHA-256. Срок действия — 30 дней; отзыв токена, блокировка владельца и сброс его пароля действуют сразу.

## Маршруты

| Метод | Путь | Роли |
|---|---|---|
| `POST` | `/api/create_user` | Super Admin |
| `PUT` | `/api/users/{id}/edit_user` | Super Admin |
| `PATCH` | `/api/users/{id}/block` | Super Admin |
| `POST` | `/api/create_fund` | Super Admin |
| `PATCH` | `/api/funds/{id}/archive` | Super Admin |
| `POST` | `/api/rights` | Super Admin |
| `DELETE` | `/api/rights/{user_id}/{fund_id}` | Super Admin |
| `DELETE` | `/api/tokens/{id}` | Super Admin |
| `PUT`, `DELETE` | `/api/transactions/{id}` | Super Admin |
| `GET` | `/api/funds` | Admin, Super Admin |
| `POST` | `/api/transactions/add` | Admin, Super Admin |
| `POST` | `/api/transactions/add_transfer` | Admin, Super Admin |
| `GET` | `/api/transactions` | Admin, Super Admin |
| `PUT` | `/api/transactions/{id}/edit` | Admin, Super Admin |
| `DELETE` | `/api/transactions/{id}/delete` | Admin, Super Admin |

Cashier и Investor получают 403 на эти endpoint согласно таблице ТЗ.

## Примеры

```powershell
$base = 'http://127.0.0.1:5000'
$token = '<секрет из окна создания токена>'
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "$base/api/funds" -Headers $headers -Method Get
```

Доход или расход передаётся JSON-объектом с `fund_id`, `type`, `money` (целое minor units), `pay_type`, `name`, `description`. Перевод использует `from_fund_id`, `to_fund_id`, `money`, при необходимости `name`, `description`, `pay_type`, `datetime`. Фильтры истории: `date_from`, `date_to`, `type`, `pay_type`, `fund_id`.

Пример дохода:

```json
{"fund_id":1,"type":"income","money":125050,"pay_type":"Kaspi","name":"Оплата","description":"Комментарий"}
```

Пример перевода:

```json
{"from_fund_id":1,"to_fund_id":2,"money":50000,"pay_type":"Внутренний перевод","name":"Пополнение"}
```

Для пользователя используются `username`, `fullname`, точная роль и `password`; для блокировки — `{"is_active":false}`. Для фонда используются `name`, `description`, `type`; для Rights — `user_id` и `fund_id`.

Успешные коды: 200 чтение/изменение, 201 создание, 204 удаление. Ошибки: 400 неверные данные, 401 отсутствующий/просроченный токен, 403 роль или Rights, 404 недоступная запись, 409 конфликт/архив, 415 неверный Content-Type. Тело ошибки: `{"error":"описание"}`.

## Безопасная проверка токена

Не вставляйте секрет в URL и не печатайте его в журнал. Проверяйте сначала `GET /api/funds`, затем разрешённую операцию и после отзыва повторяйте запрос: должен прийти 401. Токен Admin видит только назначенные фонды; отсутствие Rights на одной стороне перевода даёт 403.

---

<a id="docs-architecturemd"></a>
## Раздел 6: `docs/architecture.md`

Исходный файл: [`docs/architecture.md`](../docs/architecture.md)

# Архитектура

Cybran Software — серверное приложение на Python, Flask, SQLite, Jinja2 и локальном Bootstrap. SPA и внешние CDN не используются.

## Слои

- `run.py` создаёт приложение и запускает Waitress. При LAN-запуске он печатает выбранную SQLite-базу, адреса и QR-код.
- `app/__init__.py` содержит фабрику `create_app`, конфигурацию, CLI-команды и общие заголовки безопасности.
- `app/config.py` загружает локальный `.env`; переменные процесса имеют приоритет. Список `PAYMENT_METHODS` передаётся в шаблоны.
- `app/db.py` открывает соединение на запрос, включает foreign keys и атомарные транзакции `BEGIN IMMEDIATE`.
- `app/auth.py` обслуживает cookie-сессии HTML, CSRF, Bearer-токены API, rate limit входа и отзыв серверных сессий.
- `app/services.py` — единый слой бизнес-правил для HTML и API: роли, Rights, фонды, операции, переводы, токены и отчёты.
- `app/web.py` содержит серверные HTML-маршруты; `app/api.py` — JSON-маршруты из ТЗ.
- `app/templates/` и `app/static/` — интерфейс. Формы отправляются на Flask, JavaScript только улучшает навигацию и копирование токена.
- `tests/` используют отдельные временные SQLite-файлы и реальный Flask test client.

## Поток запроса

1. Flask принимает запрос, `load_user` проверяет cookie-сессию или Bearer-токен.
2. Маршрут проверяет CSRF для HTML либо роль для API.
3. Сервис повторно читает пользователя внутри записи, чтобы параллельная блокировка, отзыв токена или смена роли не обошлись устаревшими данными.
4. Денежная операция выполняется в одной транзакции SQLite. Для перевода создаются две связанные строки или не создаётся ни одной.
5. Ответ получает security-заголовки; API возвращает JSON с полем `error` при отказе.

## Границы развёртывания

Внутри доверенной сети допустим Waitress на `0.0.0.0` по HTTP. Для внешнего доступа нужен HTTPS reverse proxy, `COOKIE_SECURE=1`, собственный `SECRET_KEY` и закрытый от клиентов backend. `TRUSTED_PROXY_HOPS` задаётся только для контролируемой цепочки прокси.

---

<a id="docs-backup-and-restoremd"></a>
## Раздел 7: `docs/backup-and-restore.md`

Исходный файл: [`docs/backup-and-restore.md`](../docs/backup-and-restore.md)

# Резервное копирование и восстановление

## Копия

1. Остановите Waitress, чтобы не копировать файл во время записи.
2. Посмотрите в терминале фактический путь после `SQLite база: ...` и подставьте его в `$databasePath`.
3. Создайте защищённый каталог и скопируйте SQLite вместе с ключом cookie:

```powershell
$databasePath = 'instance\cybran.sqlite3'
$backupStamp = Get-Date -Format yyyyMMdd-HHmmss
New-Item -ItemType Directory -Force backups | Out-Null
Copy-Item $databasePath "backups\cybran-$backupStamp.sqlite3"
Copy-Item instance\session.key "backups\session-$backupStamp.key"
```

Каталог `backups/` не должен попадать в Git. Ключ нужен для сохранения действующих cookie; если ключ не восстановить, пользователи просто войдут заново.

## Проверка копии

```powershell
$backupPath = 'backups\cybran-YYYYMMDD-HHmmss.sqlite3'
.\.venv\Scripts\python.exe -c "import sqlite3,sys; db=sqlite3.connect(sys.argv[1]); print(db.execute('PRAGMA integrity_check').fetchone()[0]); print(list(db.execute('PRAGMA foreign_key_check'))); db.close()" $backupPath
```

Ожидается `ok` и пустой список внешних ключей.

## Восстановление

Остановите приложение, сохраните повреждённый файл отдельно, скопируйте проверенную резервную копию в путь `CYBRAN_DATABASE`, при необходимости верните `instance/session.key`, затем запустите приложение и проверьте вход, баланс, Rights и API. Не восстанавливайте копию поверх работающего процесса.

---

<a id="docs-configurationmd"></a>
## Раздел 8: `docs/configuration.md`

Исходный файл: [`docs/configuration.md`](../docs/configuration.md)

# Конфигурация

Настройки читаются из `.env` в корне проекта. Файл `.env` игнорируется Git; шаблон `.env.example` можно копировать без секретов. Переменные процесса PowerShell всегда имеют приоритет.

| Переменная | Значение по умолчанию | Назначение |
|---|---|---|
| `CYBRAN_DATABASE` | `instance/cybran.sqlite3` | Путь к SQLite. Относительный путь из `.env` считается от корня проекта. Значение из PowerShell считается от текущего каталога. |
| `PAYMENT_METHODS` | `Наличные,Kaspi,Карта` | Быстрые способы оплаты и подсказки интерфейса. |
| `HOST` | `0.0.0.0` | Адрес Waitress; `127.0.0.1` ограничивает доступ этим компьютером. |
| `PORT` | `5000` | TCP-порт Waitress. |
| `MOBILE_IP` | пусто | Явный LAN-адрес для QR, если автоопределение выбрало не тот интерфейс. |
| `COOKIE_SECURE` | `0` | При `1` cookie отправляется только по HTTPS. Для production за HTTPS ставьте `1`. |
| `SECRET_KEY` | случайный `instance/session.key` | Ключ подписания cookie. В production задайте собственный защищённый секрет. |
| `TRUSTED_PROXY_HOPS` | `0` | Число контролируемых proxy-hop для `X-Forwarded-*`; не увеличивайте при прямом доступе клиентов к backend. |

## Способы оплаты

`PAYMENT_METHODS=Наличные,Kaspi,Карта,СБП` создаёт четыре кнопки/подсказки на формах кассира, операции и фильтрах. Пустые элементы удаляются, повторы объединяются, а пустая настройка возвращает безопасный список по умолчанию. Это только удобство интерфейса: API и ручной ввод принимают любой непустой `pay_type` длиной до 50 символов по ТЗ.

После изменения `.env` перезапустите `run.py`. Рабочую базу не переключайте удалением файла: сначала проверьте напечатанный путь.

---

<a id="docs-databasemd"></a>
## Раздел 9: `docs/database.md`

Исходный файл: [`docs/database.md`](../docs/database.md)

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

---

<a id="docs-decisionsmd"></a>
## Раздел 10: `docs/DECISIONS.md`

Исходный файл: [`docs/DECISIONS.md`](../docs/DECISIONS.md)

# Решения по неоднозначностям ТЗ

Источник бизнес-логики — «ТЗ для Бубелиса Йонаса.pdf», страницы 1–10. Пользовательский `goal-objective.md` отдельно задает стек, меры безопасности, атомарность и порядок приемки. Ниже фиксируются минимальные способы совместить связанные фрагменты PDF, не вводя новые роли, финансовые сущности или бизнес-процессы. Документ описывает целевое решение; факт реализации и проверки отражается отдельно в `REQUIREMENTS_CHECKLIST.md`.

## D01. Две записи межфондового перевода

**Основание:** PDF 4 перечисляет тип `inter-transaction`; PDF 8 требует создать две записи в одной DB-транзакции, обе с `from_fund_id=X` и `to_fund_id=Y`, и допускает для каждой записи тип `inter-transaction` вместо `expense`/`income`. PDF 7–8 запрещает включать внутреннее перемещение во внешние доходы и расходы компании.

**Решение:** обе записи имеют тип `inter-transaction`, общие сумму, источник, получателя, автора, описание и время. Технический `transfer_id` связывает пару, `transfer_side` различает `debit` и `credit`. Эти поля дополняют техническую модель, но не создают новый пользовательский тип операции. Debit уменьшает остаток только источника, credit увеличивает остаток только получателя. Обычный income относится к получателю, expense — к источнику. Денежная величина не применяется к обоим фондам для каждой из двух строк, иначе перевод был бы учтен дважды.

Создание, изменение и удаление пары выполняются атомарно. Обращение к любому ID пары при коррекции/удалении обрабатывает обе записи. Admin должен иметь Rights на все затрагиваемые фонды как до, так и после изменения. В глобальных доходах, расходах, обороте, чистом потоке и динамике внешних поступлений участвуют только обычные income/expense. Перевод меняет реальные остатки фондов, в том числе при пересечении границы for_stats/no_stats, но не становится внешним доходом или расходом.

**Приемка:** ровно две согласованные строки; X − M и Y + M; ошибка при второй записи откатывает первую; изменение/удаление пары не оставляет половину; межфондовая операция не удваивает KPI.

## D02. Возможности Cashier на страницах 2 и 6

**Основание:** общее описание PDF 2 разрешает доходы, упоминает черновики расходов и запрещает редактирование/удаление. Подробная панель PDF 6 прямо требует рабочую форму expense и допускает отмену только своей последней ошибочной транзакции либо ее пометку для Admin; чужие записи read-only.

**Решение:** более конкретный сценарий PDF 6 определяет исключения к общему описанию: Cashier создает income и expense в своих фондах; обычное редактирование запрещено; доступна отдельная отмена последней собственной ошибочной записи. Выбирается разрешенный ТЗ вариант отмены без дополнительной системы черновиков/согласований. Последняя запись определяется по факту создания, а не по редактируемой дате операции. Проверка выполняется на сервере и повторяется перед удалением; принадлежность автору и актуальное право на фонд обязательны. Межфондовые переводы Cashier запрещены.

**Граница интерпретации:** PDF не задает ограничение отмены рамками календарного дня или отдельного фонда. Такие ограничения не добавляются. Последняя собственная запись понимается как последняя созданная этим Cashier запись, а не последняя после произвольного фильтра истории. История смен — дневное представление существующих транзакций; таблица смен, открытие/закрытие кассы и кассовые остатки смен не вводятся.

## D03. Investor: глобальные данные, детализация и Rights

**Основание:** PDF 2 разрешает детальную историю фондов, «к которым у него есть доступ». PDF 6–7 описывает глобальную панель, таблицу всех for_stats, переход к истории и экспорт «по всем фондам for_stats». PDF 7 отдельно говорит, что Investor физически не видит no_stats.

**Решение:** общий dashboard и глобальная выгрузка агрегируют/содержат все for_stats, как прямо сказано в отчетности. Переход к отдельной полной истории и обычный просмотр транзакций ограничены пересечением **Rights ∩ for_stats**, сохраняя ограничение PDF 2. Таблица глобального dashboard может показывать агрегаты фонда без разрешения на отдельную историю; ссылка детализации доступна только при Rights. Выдача Rights на no_stats не делает такой фонд видимым Investor. Super Admin имеет полный аудит, но его Global Dashboard использует тот же фильтр for_stats.

**Оставшаяся смысловая граница:** PDF 7 можно прочитать и как разрешение Investor открывать любую строку глобальной таблицы. Выбран более узкий доступ к подробной истории из явно указанного PDF 2 ограничения; он не урезает прямо требуемые глобальные агрегаты и выгрузку всех for_stats. Это документированное разрешение противоречия, а не утверждение, что PDF буквально описывает данную комбинацию маршрутов.

В ленте и выгрузках нельзя раскрывать имя/ID no_stats через вторую сторону перевода. Неавторизованный counterpart показывается нейтрально, без имени и ссылки. Исходные данные остаются доступны Super Admin. Для Admin/Cashier аналогично не раскрывается название чужого фонда через перевод, одна сторона которого им доступна.

## D04. API-роли и отсутствие API-таблиц Cashier/Investor

**Основание:** API-раздел PDF 8–9 содержит только таблицы Super Admin и Admin; PDF 10 содержит только стек. PDF 8 требует 403, если роль не указана в списке разрешенных для endpoint. Super Admin имеет доступ ко всем endpoints.

**Решение:** ровно 16 обязательных method/path из PDF сохраняют имена и методы. Первые 10 доступны только Super Admin; 6 Admin endpoints доступны Admin и Super Admin. Cashier/Investor получают 403 при обращении к перечисленным API endpoints с валидным токеном. Их UI-возможности из PDF 6–7 реализуются защищенными HTML routes и не расширяют API allowlist автоматически.

ТЗ требует интерфейс генерации токенов, сброса паролей, редактирования фондов и экспорта, но не задает для них API paths. Они реализуются в UI; дополнительные API paths не выдумываются для подмены обязательных. Для Bearer-аутентификации отсутствие/ошибка/отзыв токена означает 401; 403 означает, что пользователь определен, но роль или Rights запрещают действие.

## D05. Пароль `sha256` и безопасное хранение

**Основание:** PDF 3 у `Users.password_hash` стоит комментарий `sha256`, без формата хэша, соли или алгоритма растяжения; PDF 4 требует проверять пароль по хэшу. Пользовательская Цель §19 требует защищенную аутентификацию.

**Решение:** пароль хранится как соленый PBKDF2-HMAC-SHA256 в строке не длиннее 256 символов. SHA-256 сохраняется в качестве хэш-примитива; случайная соль и растяжение являются технической защитой, а не изменением бизнес-процесса. Несоленый одиночный SHA-256 для пароля не используется. Для высокоэнтропийного 128-символьного API token сохраняется именно SHA-256, как прямо указано в PDF 3. Пароль и токен не используют общий формат хранения.

## D06. `active` и `is_active`, архив фондов

**Основание:** PDF 3 называет флаг ApiTokens `active`, а PDF 5, 9 описывает отзыв через `is_active=False`. Флаги Users/Funds отсутствуют в ранней схеме PDF 3, но явно нужны на PDF 5 и 8.

**Решение:** в базе используются `Users.is_active`, `Funds.is_active`, а для ApiTokens — поле `active` из схемы PDF 3. Все операции отзыва читают/пишут один и тот же флаг; отдельные независимые `active` и `is_active` для токена не создаются. API и документация явно называют используемый формат.

Архивирование — изменение флага, без физического удаления фонда или операций. Новые записи в архивный фонд не создаются; история и рассчитанные финансовые остатки сохраняются. Тип for_stats/no_stats продолжает определять участие архивного фонда в сводной исторической отчетности: архив не является командой стереть его деньги из KPI. Возможность глобальной коррекции прошлых записей Super Admin сохраняется. Отдельный жизненный цикл удаления/восстановления фондов ТЗ не задает.

## D07. Точные денежные значения и минимальная валидация

**Основание:** PDF 4 задает `money: int`, PDF 8 — суммы в minor units, Цель §9 запрещает float. PDF 1–2 различает доход и расход типом операции.

**Решение:** SQLite хранит INTEGER; расчеты выполняются целыми числами; API принимает JSON integer, отличая его от bool. Направление задает type/сторона перевода, сумма — положительная целая величина. Проверяются границы SQLite INTEGER и арифметики. Строковый ввод HTML переводится в integer без float. Интерфейс явно объясняет единицу ввода; валюта, обменные курсы и мультивалютность не добавляются.

ТЗ не требует запрета отрицательного остатка, лимитов расходов, резервирования или наличия достаточного баланса; такие бизнес-ограничения не вводятся. Положительность суммы — защита от двусмысленного направления, а не запрет расхода сверх остатка. Перевод между одним и тем же фондом отклоняется как некорректное межфондовое движение. Для income/expense обязателен непустой pay_type, строковое поле допускает способы помимо трех примеров интерфейса.

## D08. KPI, период и чистая прибыль

**Основание:** PDF 6 требует «Доход за месяц», «Расход за месяц», «Чистая прибыль», а PDF 7 определяет оборот за выбранный период как сумму income и чистый поток как оборот минус expense.

**Решение:** общий баланс — текущие остатки всех for_stats; доход/расход/чистый поток выбранного периода — внешние income/expense за этот период. Месячные KPI относятся к текущему календарному месяцу отдельно от пользовательского периода. В доступной модели чистая прибыль = внешний income − внешний expense; начисления, налоги, дебиторская задолженность и бухгалтерские показатели не вводятся. Границы дат включают выбранные календарные дни целиком и единообразны у истории, CSV и XLSX.

Распределение денег по фондам отображает фактические остатки. У круга нет корректной отрицательной доли, поэтому при отрицательных остатках диаграмма сопровождается явным состоянием/пояснением и таблицей, а не превращает отрицательные деньги в положительные и не скрывает их из KPI. Нулевая сумма отображается как пустое распределение.

## D09. Роль автора при редактировании Admin

**Основание:** PDF 6 и 9 разрешает Admin менять только свою транзакцию или транзакцию Cashier в своем фонде. Схема PDF 4 хранит `user_id`, но не снимок роли автора на дату создания. PDF 5 позволяет Super Admin менять роли.

**Решение:** право на собственную запись проверяется по author user_id; право на запись Cashier определяется ролью связанного пользователя из Users на момент запроса. Отдельная историческая роль, журнал ролей или новая сущность не добавляются, поскольку ТЗ этого не задает. Проверка Rights обязательна независимо от авторства. Технические ограничения пары перевода не дают менять недоступный фонд через второй ID.

## D10. Проверяемость и границы требований

Каждый пункт checklist имеет отдельные статусы извлечения требования, реализации и проверки. Проверка не отмечается выполненной по одному только наличию тестовой функции: нужен ее успешный запуск. PDF не задает API JSON response schema, CSS-тему, часовой пояс, длительность сессии, пагинацию, тестовые учетные записи или внутренние имена модулей. Эти технические параметры описываются в README/коде и не выдаются за дополнительные бизнес-требования. Не добавляются CRM клиентов, склад, счета-фактуры, платежные шлюзы, новые роли, обязательные внешние сервисы или финансовые правила отсутствующие в ТЗ.

## D11. Защита доступа Super Admin

**Основание:** PDF 5 и 8 требует блокировку/разблокировку пользователей и смену роли, но не уточняет самоблокировку и минимальное число активных Super Admin. Пользователь отдельно сообщил о случайной самоблокировке и потребовал исключить такое состояние.

**Решение:** активный Super Admin не может заблокировать собственную учётную запись или изменить её роль. Любое изменение другого пользователя дополнительно проверяет, что в базе останется хотя бы один активный Super Admin. Проверка выполняется внутри `BEGIN IMMEDIATE`, поэтому два последовательных или конкурирующих изменения не могут оставить систему без управляющей учётной записи. Защита одинакова для HTML и REST API; интерфейс скрывает опасное действие и объясняет причину, а backend возвращает 409 при прямом запросе.

Это правило сохраняет доступ к уже требуемой ТЗ функции управления и не добавляет роль, сущность или финансовое поведение.

## D12. Управляемые сессии и 24-часовое завершение

**Основание:** пользователь потребовал дать Super Admin просмотр и прерывание активных сессий и завершать сессии раз в 24 часа. PDF длительность и серверное хранение browser-сессий не определяет.

**Решение:** каждый успешный вход создаёт отдельную server-side запись со случайным идентификатором, от которого в SQLite хранится только SHA-256. Cookie подписана Flask, а запрос дополнительно проверяется по записи, состоянию пользователя, `auth_version`, времени отзыва и абсолютному `expires_at`. Срок равен ровно 24 часам с момента конкретного входа и не продлевается активностью. Это предсказуемо завершает все сессии не позднее чем через 24 часа без единого общего момента, который мог бы одновременно выбросить пользователей посреди работы.

Super Admin видит только служебные метаданные: пользователя, IP, устройство и времена; токен и hash не отображаются. Доступны завершение одной сессии, всех кроме текущей и абсолютно всех. Завершение собственной текущей сессии сразу очищает cookie; logout также отзывает запись на сервере. Сброс пароля инвалидирует прежние browser-сессии через `auth_version` и отзывает API-токены пользователя.

---

<a id="docs-deploymentmd"></a>
## Раздел 11: `docs/deployment.md`

Исходный файл: [`docs/deployment.md`](../docs/deployment.md)

# Развёртывание

## Локальная сеть

Для небольшой доверенной сети достаточно Waitress:

```powershell
.\.venv\Scripts\python.exe run.py
```

По умолчанию приложение слушает `0.0.0.0:5000` и печатает QR. Откройте порт только в частном профиле Windows Firewall. HTTP по LAN не предназначен для публичного Wi-Fi.

## Production

1. Создайте отдельное виртуальное окружение и установите закреплённый `requirements.txt`. В него входит `pytest` для приёмочных проверок; на production его можно не загружать только после отдельной проверки минимального набора Flask/openpyxl/waitress/qrcode.
2. Скопируйте `.env.example` в защищённый `.env` вне Git.
3. Задайте непредсказуемый `SECRET_KEY`, постоянный `CYBRAN_DATABASE`, `COOKIE_SECURE=1` и нужный `TRUSTED_PROXY_HOPS`.
4. Запускайте Waitress за HTTPS reverse proxy. Backend должен быть недоступен клиентам в обход proxy.
5. Храните `instance/*.sqlite3` и `instance/session.key` на постоянном диске, ограничьте права каталога и регулярно делайте резервные копии.
6. Запускайте без Flask debug/reloader. После изменения `.env` перезапускайте процесс.

В текущей небольшой конфигурации статика отдаётся Flask/Waitress. При росте нагрузки её можно вынести в proxy после проверки CSP и путей, не меняя API.

## Каталоги и журналы

Записываемыми должны быть только каталог `instance/` с SQLite и `session.key`, а также каталог резервных копий, если он выбран операциями. Waitress пишет доступный вывод в stdout/stderr; при запуске как службы направьте его в журнал службы и настройте ротацию средствами ОС. Не сохраняйте в логах пароли, Bearer-токены и содержимое cookie.

## Проверка после запуска

Откройте `/login`, войдите тестовой учётной записью, проверьте `flask --app app routes`, создание одной операции и `PRAGMA integrity_check`. Затем убедитесь, что HTTPS-прокси передаёт только ожидаемые `X-Forwarded-*` и что backend недоступен напрямую.

## Обновление и откат

Перед обновлением остановите процесс, сохраните SQLite и `session.key`, установите зависимости, запустите `init-db` (он не удаляет данные), выполните тесты и только затем запустите новую версию. Для отката верните предыдущий код и совместимую резервную копию базы.

---

<a id="docs-financial-logicmd"></a>
## Раздел 12: `docs/financial-logic.md`

Исходный файл: [`docs/financial-logic.md`](../docs/financial-logic.md)

# Финансовая логика

Сумма в HTML вводится в основных единицах с двумя знаками после запятой. В сервисы и SQLite она попадает как целое число minor units: `1250,50` превращается в `125050`. Это исключает ошибки двоичной арифметики.

## Операции

- Доход имеет только `to_fund_id` и увеличивает баланс фонда.
- Расход имеет только `from_fund_id` и уменьшает баланс.
- `pay_type` обязателен и ограничен 50 символами; список быстрых вариантов настраивается через `PAYMENT_METHODS`.
- Архивный фонд сохраняет историю и баланс, но блокирует новые записи для обычных ролей.

## Перевод

Межфондовый перевод создаёт две строки `inter-transaction` с одинаковым `transfer_id`: `debit` списывает источник, `credit` зачисляет получателя. Пара создаётся и изменяется внутри одной транзакции `BEGIN IMMEDIATE`. Если вторая строка не проходит проверку, откатывается первая. В журнале и экспорте пара показывается как одна операция; во внешние доходы и расходы перевод не входит.

Admin должен иметь Rights на оба активных фонда; Super Admin имеет доступ ко всем фондам. Нельзя переводить в тот же фонд. При редактировании или удалении любой стороны сервис находит `transfer_id` и атомарно меняет или удаляет обе строки.

## Отчётность

`for_stats` участвует в общей сводке и экспорте Investor. `no_stats` может использоваться операционно, но скрыт из сводной отчётности. Баланс — текущий итог журнала; оборот, расходы и чистый поток считаются за выбранный период. Границы дат включают весь выбранный день, время в SQLite хранится в UTC.

---

<a id="docs-installationmd"></a>
## Раздел 13: `docs/installation.md`

Исходный файл: [`docs/installation.md`](../docs/installation.md)

# Установка и первый запуск

Инструкция рассчитана на Windows PowerShell и чистую рабочую копию проекта.

## Получение проекта

```powershell
git clone <repository-url> Cybran_Software
cd Cybran_Software
```

Если проект уже открыт в каталоге, начните с создания виртуального окружения.

## Установка

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Откройте `.env` и задайте `CYBRAN_DATABASE`. Относительный путь из `.env` считается от корня проекта, поэтому запуск из другой папки не выбирает случайную базу. Переменная, заданная в текущем окне PowerShell, имеет приоритет над `.env` и считается от текущего каталога.

## Создание базы и администратора

```powershell
.\.venv\Scripts\python.exe -m flask --app app init-db
.\.venv\Scripts\python.exe -m flask --app app create-superadmin
```

`create-superadmin` интерактивно запросит логин и пароль. В исходниках нет рабочего пароля. Повторный `init-db` безопасен: существующие таблицы и данные сохраняются.

Проверка чистой установки выполняется на отдельном пути базы. В PowerShell задайте переменную и создайте каталог:

```powershell
New-Item -ItemType Directory -Force tmp | Out-Null
$env:CYBRAN_DATABASE = Join-Path (Get-Location) 'tmp\clean-install.sqlite3'
```

Выполните обе команды выше, войдите созданной учётной записью, затем удалите временный файл и закройте окно PowerShell. Рабочую `instance/` для этой проверки не используйте.

## Запуск

```powershell
.\.venv\Scripts\python.exe run.py
```

Терминал напечатает строку `SQLite база: ...`, локальные адреса и QR-код. Телефон и компьютер должны быть в одной сети. Для работы только на компьютере задайте `HOST=127.0.0.1`; для другого порта — `PORT=5001`. `MOBILE_IP` позволяет явно указать адрес мобильной точки.

## Демо

Демо создаётся только отдельной командой в пустой базе:

```powershell
.\.venv\Scripts\python.exe -m flask --app app seed-demo
```

Команда записывает простые локальные пароли в `instance/demo-access.txt`. Демо-база и эти пароли не предназначены для production. Запуск сервера не добавляет демоданные автоматически.

---

<a id="docs-manual-test-planmd"></a>
## Раздел 14: `docs/MANUAL_TEST_PLAN.md`

Исходный файл: [`docs/MANUAL_TEST_PLAN.md`](../docs/MANUAL_TEST_PLAN.md)

# Cybran Software — полный сценарий ручной приемки

Версия сценария: 2026-10-07. Этот документ рассчитан на текущую очищенную демонстрационную базу. В ней уже есть четыре пользователя, но нет фондов, прав, токенов и финансовых операций.

Не меняйте порядок основных разделов: контрольные суммы ниже зависят от последовательности операций. В каждом пункте отметьте результат: `[x]` — пройдено, `[!]` — дефект, `[—]` — не проверялось. При дефекте сохраните роль, URL, введенные данные, ожидаемый и фактический результат, время UTC и снимок экрана.

## 1. Исходные условия

### Адреса

- Компьютер: `http://127.0.0.1:5000`
- Локальная сеть: `http://192.168.6.139:5000`
- Мобильная точка Windows: `http://192.168.137.1:5000`
- QR-код и адреса отображаются в нижнем терминале. Сервер должен оставаться запущенным.

### Учетные записи

| Роль | Логин | Пароль |
|---|---|---|
| Super Admin | `superadmin` | `superadmin123` |
| Admin | `admin` | `admin123` |
| Cashier | `cashier` | `cashier123` |
| Investor | `investor` | `investor123` |

Простые пароли используются только в локальной демонстрационной базе.

### Ожидаемое начальное состояние

| Таблица/объект | Количество |
|---|---:|
| Users | 4 |
| Funds | 0 |
| Rights | 0 |
| ApiTokens | 0 |
| Transactions | 0 |

### Подготовка браузеров

1. На компьютере откройте приложение в обычном окне.
2. Для параллельной проверки ролей используйте отдельные профили браузера или приватные окна. Один браузерный профиль хранит одну активную сессию.
3. На телефоне отсканируйте QR-код. Телефон и компьютер должны быть в одной сети.
4. Запишите текущую дату, отображаемую в интерфейсе. Далее она обозначается `D`; все границы дат работают в UTC.

Критерии:

- [ ] Страница входа открывается по `127.0.0.1`.
- [ ] Страница входа открывается по LAN-адресу.
- [ ] На телефоне открывается та же страница без горизонтальной прокрутки всей страницы.
- [ ] В консоли сервера нет traceback/ошибки 500.

## 2. Вход, выход и начальный экран

### M-01. Неверные учетные данные

1. Введите логин `admin` и пароль `wrong-password`.
2. Нажмите «Войти в систему».

Ожидается:

- [ ] Ответ остается на странице входа.
- [ ] Показано сообщение о неверном логине/пароле или блокировке.
- [ ] Внутренние данные, хэш пароля и traceback не показываются.

### M-02. Вход каждой роли

По очереди войдите каждой из четырех учетных записей и после проверки нажимайте «Выйти из системы».

Ожидается:

- [ ] `superadmin` попадает на «Обзор финансов».
- [ ] `admin` попадает на «Мои фонды» и видит пустое состояние.
- [ ] `cashier` попадает на «Приём оплаты» и видит сообщение об отсутствии доступных фондов.
- [ ] `investor` попадает на «Обзор финансов» в режиме «Только просмотр».
- [ ] После выхода защищенная страница снова требует вход.

### M-03. Начальная пустая база Super Admin

Войдите как `superadmin`.

Ожидается:

- [ ] Дашборд: баланс, оборот, расходы и чистый поток равны `0,00`.
- [ ] В разделе «Все фонды» показано пустое состояние.
- [ ] В разделе «Операции» нет записей.
- [ ] В разделе «Пользователи» ровно четыре исходных пользователя.
- [ ] В разделе «API-токены» нет токенов.

## 3. Создание контрольных фондов

Войдите как `superadmin`, откройте «Все фонды» → «Создать фонд». Создайте фонды строго в следующем порядке.

| Порядок | Название | Описание | Отчетность | Ожидаемый ID в чистой базе |
|---:|---|---|---|---:|
| 1 | `Основная касса` | `Ежедневные поступления и расходы` | Включать | 1 |
| 2 | `Разработка` | `Проекты разработки` | Включать | 2 |
| 3 | `Маркетинг` | `Продвижение компании` | Включать | 3 |
| 4 | `Технический фонд` | `Внутренние технические операции` | Исключить | 4 |

После каждого создания ожидается сообщение «Фонд сохранён».

### M-04. Проверка списка фондов

Ожидается:

- [ ] В списке четыре карточки.
- [ ] Первые три помечены «В отчётности».
- [ ] «Технический фонд» помечен «Вне отчётности».
- [ ] Баланс каждого фонда `0,00`, операций `0`.
- [ ] Общий баланс доступных фондов Super Admin `0,00`.

### M-05. Редактирование метаданных фонда

1. Откройте «Маркетинг» → «Настроить».
2. Измените описание на `Продвижение компании — ручная проверка`.
3. Сохраните.

Ожидается:

- [ ] Новое описание показано на карточке и странице фонда.
- [ ] Тип фонда остался `for_stats`.
- [ ] Баланс и история не изменились.

## 4. Проверка отсутствия прав до назначения

До выдачи Rights по очереди войдите как `admin` и `cashier`.

Ожидается:

- [ ] Admin не видит ни одного фонда.
- [ ] Admin не может провести операцию или перевод без доступных фондов.
- [ ] Cashier видит «Нет доступных фондов».
- [ ] Прямой переход Admin на `/funds/1` возвращает страницу `403`.
- [ ] Прямой переход Cashier на `/funds/1` возвращает страницу `403`.

Investor до назначения Rights:

- [ ] Глобальный дашборд содержит три фонда `for_stats` с нулевыми агрегатами.
- [ ] Названия фондов без Rights не ведут на детализацию.
- [ ] Раздел «Мои фонды» пуст.
- [ ] «Технический фонд» нигде не показан.

## 5. Настройка Rights

Войдите как `superadmin`, откройте «Права доступа». Для каждого пользователя выберите пользователя, отметьте фонды и нажмите «Сохранить права».

| Пользователь | Основная касса | Разработка | Маркетинг | Технический фонд |
|---|:---:|:---:|:---:|:---:|
| `admin` | ✓ | ✓ |  |  |
| `cashier` | ✓ | ✓ |  |  |
| `investor` | ✓ | ✓ |  |  |

### M-06. Сохранение и повторное открытие

- [ ] После каждого сохранения показано успешное сообщение.
- [ ] Повторный выбор пользователя показывает те же отметки.
- [ ] Super Admin видит пояснение, что его полный доступ не зависит от Rights.

### M-07. Немедленное применение прав

В новых приватных окнах войдите как Admin, Cashier и Investor.

Ожидается:

- [ ] Admin видит только «Основная касса» и «Разработка».
- [ ] Cashier может выбрать только эти два фонда.
- [ ] Investor видит детализацию только этих двух фондов.
- [ ] Admin/Cashier не видят «Маркетинг» и «Технический фонд».
- [ ] Investor видит «Маркетинг» в глобальных агрегатах, но без ссылки на историю.
- [ ] Прямые URL `/funds/3` и `/funds/4` для Investor возвращают `403`.

### M-08. Отзыв права

1. Временно снимите у Cashier отметку «Разработка» и сохраните.
2. Обновите страницу Cashier.
3. Убедитесь, что осталась только «Основная касса».
4. Верните право на «Разработку» и снова обновите страницу.

Ожидается:

- [ ] Отзыв применяется без повторного входа.
- [ ] Возврат права также применяется сразу.

## 6. Базовые операции Admin

Войдите как `admin`. Все операции создавайте на текущую дату `D`.

### M-09. Доход в Основную кассу

«Новая операция»:

- тип: `Доход`;
- фонд: `Основная касса`;
- сумма: `1000,00`;
- способ оплаты: `Kaspi`;
- название: `Стартовый доход`;
- комментарий: `M-09`.

Ожидается:

- [ ] Успешное сообщение.
- [ ] Баланс Основной кассы `1 000,00`.
- [ ] Автор — «Администратор фондов».

### M-10. Расход из Основной кассы

- тип: `Расход`;
- фонд: `Основная касса`;
- сумма: `200,00`;
- способ оплаты: `Карта`;
- название: `Аренда`;
- комментарий: `M-10`.

Ожидается баланс Основной кассы `800,00`.

### M-11. Доход в Разработку

- тип: `Доход`;
- фонд: `Разработка`;
- сумма: `500,00`;
- способ оплаты: `Карта`;
- название: `Оплата разработки`;
- комментарий: `M-11`.

Ожидается баланс Разработки `500,00`.

### M-12. Межфондовый перевод

Откройте «Перевести»:

- из фонда: `Основная касса`;
- в фонд: `Разработка`;
- сумма: `300,00`;
- способ оплаты оставьте пустым;
- название: `Финансирование разработки`;
- комментарий: `M-12`.

Ожидается:

- [ ] Основная касса: `500,00`.
- [ ] Разработка: `800,00`.
- [ ] Сумма двух балансов сохранилась: `1 300,00`.
- [ ] В истории перевод показан одной строкой со стрелкой между фондами.
- [ ] Способ отображается как «Внутренний перевод».
- [ ] В карточке Основной кассы счетчик операций `3`, Разработки — `2` (пара хранится двумя связанными проводками).

### Контрольная точка A

| Показатель | Ожидается |
|---|---:|
| Основная касса | `500,00` |
| Разработка | `800,00` |
| Маркетинг | `0,00` |
| Технический фонд | `0,00` |
| Global balance | `1 300,00` |
| Global turnover | `1 500,00` |
| Global expenses | `200,00` |
| Global net flow | `1 300,00` |

## 7. Операции Super Admin и граница no_stats

Войдите как `superadmin`.

### M-13. Доход Маркетинга

- Доход, фонд `Маркетинг`, сумма `700,00`, способ `Наличные`;
- название `Маркетинговый бюджет`, комментарий `M-13`.

### M-14. Доход Технического фонда

- Доход, фонд `Технический фонд`, сумма `9000,00`, способ `Наличные`;
- название `Техническое поступление`, комментарий `M-14`.

### Контрольная точка B

| Показатель | Ожидается |
|---|---:|
| Основная касса | `500,00` |
| Разработка | `800,00` |
| Маркетинг | `700,00` |
| Технический фонд | `9 000,00` |
| Сумма всех фондов Super Admin | `11 000,00` |
| Global balance (`for_stats`) | `2 000,00` |
| Global turnover | `2 200,00` |
| Global expenses | `200,00` |
| Global net flow | `2 000,00` |

Проверьте:

- [ ] Технические `9 000,00` не входят ни в один глобальный KPI.
- [ ] Техническая операция отсутствует в ленте Global Dashboard.
- [ ] Перевод `300,00` не прибавлен к turnover или expenses.
- [ ] На графике поступлений учитываются только внешние income.
- [ ] На круговой диаграмме только три фонда `for_stats`.

## 8. Работа Cashier

Войдите как `cashier`.

### M-15. Быстрый прием оплаты

На главном экране:

- фонд `Основная касса`;
- сумма `120,50`;
- способ `Наличные`;
- комментарий `Оплата клиента M-15`.

Ожидается:

- [ ] Сообщение «Оплата принята».
- [ ] Операция income видна сегодня.
- [ ] «Ваши поступления сегодня» увеличены на `120,50`.
- [ ] Баланс Основной кассы `620,50`.

### M-16. Расход кассира

Нажмите «Расход из кассы»:

- фонд `Основная касса`;
- сумма `20,50`;
- способ `Наличные`;
- название `Хозяйственные расходы`;
- комментарий `M-16`.

Ожидается баланс Основной кассы `600,00`.

### M-17. Отмена последней ошибочной операции

1. Создайте быстрый доход в «Разработку»: `9,99`, `Kaspi`, комментарий `ОШИБКА M-17`.
2. Убедитесь, что баланс Разработки стал `809,99`.
3. В строке последней собственной операции нажмите «Отменить» и подтвердите.

Ожидается:

- [ ] Ошибочная операция исчезла.
- [ ] Баланс Разработки снова `800,00`.
- [ ] У более ранних собственных и чужих записей кнопки отмены нет.
- [ ] Cashier не может редактировать или удалять чужие операции.

### M-18. История смен

Откройте «История смен».

Ожидается:

- [ ] Есть группа за дату `D` в UTC.
- [ ] Собственный доход Cashier `120,50`.
- [ ] Собственный расход Cashier `20,50`.
- [ ] В группе видны и операции других авторов в доступных фондах, но они read-only.

### M-19. Запрет перевода и управления

- [ ] В меню Cashier нет «Права доступа», «Пользователи», «API-токены».
- [ ] Прямой URL `/transfers/new` возвращает `403`.
- [ ] Прямой URL `/users` возвращает `403`.
- [ ] Прямой URL `/funds/3` возвращает `403`.

### Контрольная точка C

| Показатель | Ожидается |
|---|---:|
| Основная касса | `600,00` |
| Разработка | `800,00` |
| Маркетинг | `700,00` |
| Технический фонд | `9 000,00` |
| Global balance | `2 100,00` |
| Global turnover | `2 320,50` |
| Global expenses | `220,50` |
| Global net flow | `2 100,00` |

## 9. Фильтры истории

Проверяйте до редактирования и удаления из следующего раздела.

### M-20. Super Admin — глобальная история

Ожидается восемь логических строк: семь операций `for_stats` и одна операция Технического фонда. Перевод занимает одну строку.

Проверьте последовательно:

- [ ] Тип `Доход`: 5 строк, включая Технический фонд.
- [ ] Тип `Расход`: 2 строки.
- [ ] Тип `Перевод`: 1 строка.
- [ ] Способ `Kaspi`: «Стартовый доход».
- [ ] Фонд `Основная касса`: связанные с ним операции без раскрытия посторонних данных.
- [ ] Диапазон `D`—`D` включает весь день.
- [ ] Дата начала позже даты окончания показывает ошибку, не 500.
- [ ] «Сбросить» возвращает полную историю.

### M-21. Ограничение фильтров Admin/Cashier

Войдите как Admin и Cashier.

- [ ] В выборе фонда только «Основная касса» и «Разработка».
- [ ] Фильтр или подмена `fund_id=3` вручную не раскрывает Маркетинг и возвращает `403`.
- [ ] Техническая операция не появляется ни при каком фильтре.

## 10. Investor и Global Dashboard

Войдите как `investor`.

### M-22. Read-only интерфейс

- [ ] Видна метка «Только просмотр».
- [ ] Нет кнопок «Новая операция», «Перевод», «Изменить», «Удалить».
- [ ] Прямые POST/URL создания и редактирования недоступны (`403`).
- [ ] Раздел «Мои фонды» содержит только Основную кассу и Разработку.

### M-23. Глобальные агрегаты

Установите период, включающий дату `D`.

Ожидается контрольная точка C:

- [ ] Общий баланс `2 100,00`.
- [ ] Общий оборот `2 320,50`.
- [ ] Общие расходы `220,50`.
- [ ] Чистый денежный поток `2 100,00`.
- [ ] Если `D` относится к текущему месяцу: доход месяца `2 320,50`, расход `220,50`, чистая прибыль `2 100,00`.
- [ ] Фонды Global Dashboard: Основная касса, Разработка, Маркетинг.
- [ ] «Технический фонд» и сумма `9 000,00` отсутствуют.
- [ ] Маркетинг участвует в агрегатах, но его название не является ссылкой: у Investor нет Rights.
- [ ] Перевод отмечен как внутренний и не изменяет внешние KPI.

### M-24. Детализация Investor

- [ ] Основная касса открывается read-only.
- [ ] Разработка открывается read-only.
- [ ] `/funds/3` (Маркетинг без Rights) → `403`.
- [ ] `/funds/4` (no_stats) → `403`.

## 11. CSV и Excel

Оставаясь Investor, выберите период `D`—`D` и скачайте CSV и Excel.

### M-25. CSV

- [ ] Файл скачивается и открывается в UTF-8.
- [ ] Есть строка заголовков.
- [ ] Ровно семь логических операций `for_stats` до коррекций: четыре income, два expense и один transfer.
- [ ] Межфондовый перевод представлен одной строкой.
- [ ] Нет «Технического фонда» и суммы `900000` minor units.
- [ ] Денежные значения экспортированы целыми minor units.
- [ ] Период соответствует `D`—`D`.

### M-26. Excel

- [ ] Файл `.xlsx` открывается без восстановления/ошибок.
- [ ] Лист называется «Операции for_stats».
- [ ] Заголовок закреплен, включен автофильтр.
- [ ] Строки и значения совпадают с CSV.
- [ ] Пользовательский текст не превращается в формулу.

## 12. Коррекция операций Admin

Войдите как `admin`.

### M-27. Редактирование операции Cashier

Найдите «Приём оплаты» с комментарием `Оплата клиента M-15` и измените сумму с `120,50` на `150,50`.

Ожидается:

- [ ] Баланс Основной кассы увеличился на `30,00`: стал `630,00`.
- [ ] Автор операции остался Cashier.
- [ ] Global turnover стал `2 350,50`.
- [ ] Global balance/net flow стал `2 130,00`.

### M-28. Удаление операции Cashier

Удалите «Хозяйственные расходы» `20,50` и подтвердите.

Ожидается:

- [ ] Запись исчезла.
- [ ] Баланс Основной кассы стал `650,50`.
- [ ] Global expenses вернулись к `200,00`.
- [ ] Global balance/net flow стал `2 150,50`.

### M-29. Ограничения Admin

- [ ] Admin может редактировать собственные записи и записи Cashier в своих фондах.
- [ ] Admin не видит Маркетинг/Технический фонд.
- [ ] Прямая попытка исправить операцию Super Admin или чужого фонда возвращает `403`.
- [ ] Изменение фонда операции на недоступный фонд запрещено без частичного изменения данных.

### Контрольная точка D — итоговая финансовая база

| Показатель | Ожидается |
|---|---:|
| Основная касса | `650,50` |
| Разработка | `800,00` |
| Маркетинг | `700,00` |
| Технический фонд | `9 000,00` |
| Сумма всех фондов Super Admin | `11 150,50` |
| Global balance | `2 150,50` |
| Global turnover | `2 350,50` |
| Global expenses | `200,00` |
| Global net flow / прибыль | `2 150,50` |

## 13. Глобальная коррекция Super Admin

### M-30. Любая операция

1. Войдите как Super Admin.
2. Создайте во временных целях income `10,00` в Маркетинг с названием `Временная M-30`.
3. Измените сумму на `15,00`.
4. Удалите запись.

Ожидается:

- [ ] После создания баланс Маркетинга `710,00`.
- [ ] После редактирования `715,00`.
- [ ] После удаления снова `700,00`.
- [ ] Контрольная точка D полностью восстановилась.

### M-31. Изменение/удаление пары перевода

Этот тест меняет базовую операцию, поэтому после него восстановите исходную сумму.

1. Найдите «Финансирование разработки».
2. Измените сумму `300,00` → `250,00`.
3. Ожидайте: Основная касса `700,50`, Разработка `750,00`; общий Global balance остается `2 150,50`.
4. Верните сумму `300,00`.
5. Ожидайте возврат к `650,50` и `800,00`.

Не удаляйте базовый перевод, если хотите продолжить сверку с контрольной точкой D. Если проверяете удаление, зафиксируйте восстановленные балансы и создайте перевод заново с теми же данными.

## 14. Управление пользователями

### M-32. Поиск и фильтр

В разделе «Пользователи»:

- [ ] Поиск `кассир` находит пользователя Cashier.
- [ ] Фильтр роли `Investor` показывает только инвесторов.
- [ ] Сброс фильтров возвращает полный список.

### M-33. Создание временного пользователя

Создайте:

- полное имя `Ручной тестировщик`;
- логин `manualcash`;
- роль `Cashier`;
- пароль `manual123`.

Назначьте ему только «Основную кассу».

Ожидается:

- [ ] Вход `manualcash/manual123` успешен.
- [ ] Пользователь видит только Основную кассу.
- [ ] Разработка и административные разделы недоступны.

### M-34. Блокировка и разблокировка

1. Заблокируйте `manualcash`.
2. Попробуйте войти этим пользователем.
3. Разблокируйте.

Ожидается:

- [ ] Заблокированный пользователь не входит.
- [ ] Уже открытая сессия прекращает работать при следующем запросе.
- [ ] После разблокировки вход снова успешен.

### M-34A. Защита Super Admin от потери собственного доступа

1. Войдите как `superadmin` и откройте «Пользователи».
2. Найдите строку с меткой «Это вы».
3. Откройте редактирование собственной учётной записи.

Ожидается:

- [ ] В собственной строке нет кнопки «Заблокировать»; показано объяснение защиты.
- [ ] На странице редактирования роль собственной учётной записи недоступна для изменения.
- [ ] Имя, логин и собственный пароль по-прежнему можно менять.
- [ ] Прямой `PATCH /api/users/{свой_id}/block` с `is_active=false` возвращает HTTP `409`.
- [ ] Прямой `PUT /api/users/{свой_id}/edit_user` со сменой роли возвращает HTTP `409`.
- [ ] После обеих попыток `superadmin` остается активным Super Admin и продолжает работать.

### M-35. Сброс пароля Admin

1. Установите Admin новый пароль `admin456`.
2. Проверьте: `admin123` больше не подходит, `admin456` подходит.
3. Верните пароль `admin123`.

Ожидается:

- [ ] Старые сессии Admin инвалидированы.
- [ ] После возврата исходного пароля вход `admin/admin123` снова успешен.

### M-35A. Просмотр и одиночное завершение активной сессии

1. В обычном окне войдите как `superadmin`.
2. В приватном окне войдите второй раз как `superadmin`.
3. В обычном окне откройте «Активные сессии».
4. Сверьте обе карточки: пользователь, IP, устройство, время входа, последняя активность и автовыход.
5. У второй карточки нажмите «Завершить сессию» и подтвердите действие.
6. Обновите любую защищённую страницу в приватном окне.

Ожидается:

- [ ] Показаны две разные активные сессии, у обычного окна есть метка «Текущая сессия».
- [ ] В интерфейсе нет значения cookie, session token или его SHA-256.
- [ ] После отзыва приватное окно отправлено на `/login` с понятным сообщением.
- [ ] Обычное окно продолжает работать.
- [ ] Admin, Cashier и Investor получают HTTP 403 при прямом открытии `/sessions`.

### M-35B. Массовое завершение сессий

1. Снова создайте второй приватный вход `superadmin`.
2. В обычном окне на странице «Активные сессии» нажмите «Завершить остальные».
3. Обновите приватное и обычное окна.
4. Снова создайте второй вход, затем в обычном окне нажмите «Завершить все» и подтвердите.

Ожидается:

- [ ] «Завершить остальные» закрывает приватный вход, но сохраняет текущий обычный.
- [ ] «Завершить все» отправляет на вход оба окна, включая окно инициатора.
- [ ] После нового входа появляется новая запись с автовыходом ровно через 24 часа.
- [ ] Активность и обновление страниц не сдвигают время автовыхода.

Автоматический тест дополнительно переводит время сессии за границу `expires_at` и подтверждает отказ старой cookie без ожидания 24 часов.

## 15. Переключение отчетности и архив

### M-36. for_stats → no_stats → for_stats

1. Super Admin открывает настройки Маркетинга.
2. Выбирает «Исключить из отчётности» и сохраняет.

Ожидается без Маркетинга:

| KPI | Значение |
|---|---:|
| Global balance | `1 450,50` |
| Turnover | `1 650,50` |
| Expenses | `200,00` |
| Net flow | `1 450,50` |

- [ ] Маркетинг исчез из Global Dashboard и экспортов Investor.
- [ ] Его собственный баланс и история сохранены для Super Admin.

Верните Маркетинг в `for_stats`; контрольная точка D должна восстановиться.

### M-37. Архивирование Технического фонда

1. Откройте «Технический фонд» → «Настроить» → «Архивировать фонд».
2. Подтвердите.

Ожидается:

- [ ] Карточка помечена «В архиве».
- [ ] Баланс `9 000,00` и история сохранены.
- [ ] Создание новой операции в архивный фонд недоступно.
- [ ] Global Dashboard не меняется, так как фонд `no_stats`.
- [ ] Super Admin по-прежнему может корректировать старую транзакцию через глобальную историю.

## 16. Проверка валидации и безопасности UI

Каждую ошибку проверяйте в доступном активном фонде. После отказа убедитесь, что баланс и число операций не изменились.

### M-38. Суммы

- [ ] Пустая сумма отклоняется.
- [ ] `0` отклоняется.
- [ ] `-1` отклоняется.
- [ ] `1,001` отклоняется как дробная minor unit.
- [ ] `NaN` и `Infinity` отклоняются.
- [ ] `92233720368547758,08` отклоняется как переполнение.
- [ ] `12,34` сохраняется точно как `12,34`.

Удалите временную корректную операцию `12,34`, чтобы вернуть контрольную точку D.

### M-39. Поля и перевод

- [ ] Income/expense без способа оплаты отклоняется.
- [ ] Перевод из фонда в тот же фонд отклоняется.
- [ ] Название длиннее 50 и описание длиннее 150 символов не сохраняются.
- [ ] Неверная дата не вызывает страницу 500.

### M-40. XSS и SQL-подобный текст

Создайте временную операцию с названием `<script>alert(1)</script>` и комментарием `'; DROP TABLE Users; --`.

Ожидается:

- [ ] Скрипт не выполняется; текст показан буквально/экранирован.
- [ ] Пользователи и остальные данные остаются на месте.
- [ ] Операция удаляется обычным способом.

### M-41. CSRF

В PowerShell отправьте HTML-login без скрытого CSRF-поля:

```powershell
Invoke-WebRequest -Method Post `
  -Uri "http://127.0.0.1:5000/login" `
  -Body @{ username = "admin"; password = "admin123" } `
  -UseBasicParsing
```

Ожидается HTTP `400`, а не вход и не `500`.

### M-42. Прямые URL и IDOR

Проверить после входа соответствующей ролью:

| Роль | URL | Ожидается |
|---|---|---|
| Admin | `/users` | 403 |
| Admin | `/funds/3` | 403 |
| Cashier | `/transfers/new` | 403 |
| Cashier | `/tokens` | 403 |
| Investor | `/transactions/new` | 403 |
| Investor | `/funds/3` | 403 |
| Investor | `/funds/4` | 403 |

## 17. API-токены

Войдите как Super Admin → «API-токены».

### M-43. Однократный показ

Создайте токены для `superadmin`, `admin`, `cashier` и `investor`. Каждый секрет сразу сохраните во временные переменные PowerShell:

```powershell
$base = "http://127.0.0.1:5000"
$rootToken = "ВСТАВЬТЕ_ТОКЕН_SUPERADMIN"
$adminToken = "ВСТАВЬТЕ_ТОКЕН_ADMIN"
$cashierToken = "ВСТАВЬТЕ_ТОКЕН_CASHIER"
$investorToken = "ВСТАВЬТЕ_ТОКЕН_INVESTOR"
```

Ожидается:

- [ ] Каждый токен имеет ровно 128 символов.
- [ ] После обновления страницы секрет больше не отображается.
- [ ] В списке остаются только ID, владелец, дата и статус.
- [ ] Хэш токена нигде в UI не показан.

### Удобная функция для JSON-запросов

```powershell
function Invoke-CybranApi {
    param(
        [string]$Method,
        [string]$Path,
        [string]$Token,
        $Body = $null
    )
    $args = @{
        Method = $Method
        Uri = "$base$Path"
        Headers = @{ Authorization = "Bearer $Token" }
        ContentType = "application/json"
    }
    if ($null -ne $Body) { $args.Body = ($Body | ConvertTo-Json -Depth 6) }
    try {
        $response = Invoke-WebRequest @args -UseBasicParsing
        "HTTP $($response.StatusCode)"
        if ($response.Content) { $response.Content | ConvertFrom-Json }
    } catch {
        "HTTP $([int]$_.Exception.Response.StatusCode)"
        $_.ErrorDetails.Message
    }
}
```

### M-44. API-аутентификация и роли

```powershell
Invoke-CybranApi GET "/api/funds" $adminToken
Invoke-CybranApi GET "/api/funds" $cashierToken
Invoke-CybranApi GET "/api/funds" $investorToken
Invoke-CybranApi GET "/api/funds" "wrong-token"
```

Ожидается:

- [ ] Admin: HTTP 200, ровно Основная касса и Разработка.
- [ ] Cashier: HTTP 403.
- [ ] Investor: HTTP 403.
- [ ] Неверный/короткий токен: HTTP 401.
- [ ] Cookie-сессия браузера без Bearer-токена не авторизует API.

### M-45. Admin API — операции

Получите ID своих фондов:

```powershell
$funds = Invoke-RestMethod -Uri "$base/api/funds" -Headers @{ Authorization = "Bearer $adminToken" }
$cashId = ($funds | Where-Object name -eq "Основная касса").id
$devId = ($funds | Where-Object name -eq "Разработка").id
```

Создайте временный income `10,00` (в API сумма передается в minor units):

```powershell
$created = Invoke-RestMethod -Method Post -Uri "$base/api/transactions/add" `
  -Headers @{ Authorization = "Bearer $adminToken" } -ContentType "application/json" `
  -Body (@{ fund_id=$cashId; type="income"; money=1000; pay_type="Kaspi";
            name="API TEMP"; description="M-45" } | ConvertTo-Json)
```

Проверьте:

- [ ] HTTP 201, `money=1000`, автор — Admin.
- [ ] Баланс Основной кассы увеличился на `10,00`.

Измените сумму на `20,00`, затем удалите:

```powershell
Invoke-CybranApi PUT "/api/transactions/$($created.id)/edit" $adminToken @{ money=2000 }
Invoke-CybranApi DELETE "/api/transactions/$($created.id)/delete" $adminToken
```

- [ ] После PUT баланс отражает `20,00`.
- [ ] После DELETE контрольная точка D восстановлена.

Временный перевод `5,00`:

```powershell
$transfer = Invoke-RestMethod -Method Post -Uri "$base/api/transactions/add_transfer" `
  -Headers @{ Authorization = "Bearer $adminToken" } -ContentType "application/json" `
  -Body (@{ from_fund_id=$cashId; to_fund_id=$devId; money=500;
            description="M-45 transfer" } | ConvertTo-Json)
Invoke-CybranApi DELETE "/api/transactions/$($transfer.id)/delete" $adminToken
```

- [ ] Перевод меняет оба фонда на `5,00`, общий баланс не меняется.
- [ ] Удаление восстанавливает оба баланса.

Негативные API-проверки:

- [ ] `money=1.5`, строка `"100"`, `true`, `0`, отрицательное число → HTTP 400.
- [ ] `fund_id=3` для Admin → HTTP 403.
- [ ] Перевод в фонд 3 или из фонда 3 → HTTP 403.
- [ ] Неверный `Content-Type` → HTTP 415.
- [ ] Неизвестный ID → HTTP 404.

### M-46. Super Admin API — специальные endpoints

Создание и управление временным пользователем:

```powershell
$apiUser = Invoke-RestMethod -Method Post -Uri "$base/api/create_user" `
  -Headers @{ Authorization = "Bearer $rootToken" } -ContentType "application/json" `
  -Body (@{ username="api_temp"; fullname="API Temporary";
            password="api_temp123"; role="Cashier" } | ConvertTo-Json)

Invoke-CybranApi PUT "/api/users/$($apiUser.id)/edit_user" $rootToken `
  @{ username="api_temp"; fullname="API Temporary Updated"; role="Investor" }
Invoke-CybranApi PATCH "/api/users/$($apiUser.id)/block" $rootToken @{ is_active=$false }
Invoke-CybranApi PATCH "/api/users/$($apiUser.id)/block" $rootToken @{ is_active=$true }
```

Ожидается: создание 201, остальные изменения 200; роль/имя/active применяются сразу.

Создание фонда, Rights и архив:

```powershell
$apiFund = Invoke-RestMethod -Method Post -Uri "$base/api/create_fund" `
  -Headers @{ Authorization = "Bearer $rootToken" } -ContentType "application/json" `
  -Body (@{ name="API TEMP FUND"; description="M-46"; type="no_stats" } | ConvertTo-Json)

Invoke-CybranApi POST "/api/rights" $rootToken @{ user_id=$apiUser.id; fund_id=$apiFund.id }
Invoke-CybranApi DELETE "/api/rights/$($apiUser.id)/$($apiFund.id)" $rootToken
Invoke-CybranApi PATCH "/api/funds/$($apiFund.id)/archive" $rootToken @{}
```

Ожидается: право появляется и отзывается; фонд остается в архиве без удаления.

### M-47. Глобальное PUT/DELETE транзакции

1. С помощью `$rootToken` и `/api/transactions/add` создайте временный income в Маркетинг.
2. Измените его через `PUT /api/transactions/{id}`.
3. Удалите через `DELETE /api/transactions/{id}`.

Ожидается:

- [ ] Super Admin может изменить/удалить запись любого автора и фонда.
- [ ] После удаления контрольная точка D восстановлена.
- [ ] Admin на этих глобальных путях получает 403.

### M-48. Отзыв токена

1. В UI Super Admin найдите ID токена Admin и нажмите «Отозвать» либо вызовите `DELETE /api/tokens/{id}` с `$rootToken`.
2. Повторите `GET /api/funds` со старым `$adminToken`.

Ожидается:

- [ ] Статус токена в UI «Отозван».
- [ ] Старый токен дает HTTP 401.
- [ ] Открытый секрет/хэш не появляется.

После завершения отзовите остальные тестовые токены.

## 18. Мобильная и адаптивная проверка

### M-49. Подключение по QR

- [ ] Камера телефона распознает QR как URL `http://192.168.6.139:5000` либо адрес мобильной точки.
- [ ] Страница открывается без предупреждений приложения.
- [ ] При недоступности основного LAN телефон, подключенный к хот-споту Windows, открывает `http://192.168.137.1:5000`.

### M-50. Навигация 360–430 px

На телефоне войдите каждой ролью либо проверьте минимум Super Admin и Cashier.

- [ ] Боковое меню скрыто и открывается кнопкой.
- [ ] Нажатие вне меню и Escape закрывают его.
- [ ] Карточки KPI перестраиваются без выхода за экран.
- [ ] Формы не обрезаны; все поля и кнопки доступны.
- [ ] Таблицы прокручиваются внутри своего блока, вся страница не имеет горизонтального overflow.
- [ ] Кнопки имеют удобную область касания.
- [ ] Cashier может выбрать фонд, сумму и способ оплаты одной рукой.
- [ ] После поворота телефона интерфейс остается рабочим.

### M-51. Desktop

- [ ] Навигация постоянно видна.
- [ ] График и круговая диаграмма не перекрываются.
- [ ] Длинные описания не ломают карточки и таблицы.
- [ ] Tab-навигация показывает фокус; Enter активирует ссылки/кнопки.
- [ ] Ссылка «Перейти к содержимому» появляется при фокусе с клавиатуры.

## 19. Финальная сверка

Перед завершением убедитесь, что все временные финансовые операции `TEMP`, M-30, M-38 и M-40 удалены, перевод M-12 восстановлен до `300,00`, а Маркетинг снова `for_stats`.

### Ожидаемые итоговые данные

| Объект | Ожидается |
|---|---:|
| Основная касса | `650,50` |
| Разработка | `800,00` |
| Маркетинг | `700,00` |
| Технический фонд (архив) | `9 000,00` |
| Global balance | `2 150,50` |
| Global turnover | `2 350,50` |
| Global expenses | `200,00` |
| Global net flow | `2 150,50` |
| Обычных логических операций `for_stats` | 5 |
| Межфондовых логических операций | 1 |
| Логических строк в Global/экспорте | 6 |

Дополнительные ожидаемые артефакты после полного сценария:

- пользователь `manualcash` существует и разблокирован;
- пользователь `api_temp` существует;
- фонд `API TEMP FUND` существует в архиве, без операций;
- все тестовые API-токены отозваны;
- Технический фонд архивирован;
- основная финансовая контрольная точка D сохранена.

### Финальный чек-лист приемки

- [ ] Все четыре роли входят и получают разные панели.
- [ ] Backend реально запрещает чужие фонды и действия.
- [ ] Income/expense корректно меняют один баланс.
- [ ] Transfer корректно меняет два баланса и не меняет общий внешний поток.
- [ ] Cashier отменяет только последнюю собственную ошибочную операцию.
- [ ] Investor полностью read-only и не видит no_stats.
- [ ] Dashboard совпадает с ручной арифметикой.
- [ ] CSV и Excel совпадают с выбранным периодом и не содержат no_stats.
- [ ] Токены показываются один раз, роли/Rights действуют в API.
- [ ] Отозванный токен и заблокированный пользователь не работают.
- [ ] Архив сохраняет историю и запрещает новые операции.
- [ ] Мобильная версия открывается по QR и остается удобной.
- [ ] Нет страниц 500, traceback, фиктивных кнопок или незавершенных маршрутов.

## 20. Шаблон регистрации дефекта

```text
ID проверки:
Дата/время UTC:
Роль и логин:
Устройство/браузер:
URL:
Предусловия:
Шаги воспроизведения:
Введенные данные:
Ожидаемый результат:
Фактический результат:
HTTP-код (если известен):
Скриншот/файл экспорта:
Повторяемость: всегда / иногда / один раз
Критичность: blocker / high / medium / low
```

Работа считается принятой, когда все обязательные пункты отмечены `[x]`, контрольная точка D совпадает по всем суммам, временные операции удалены, а открытые дефекты уровня blocker/high отсутствуют.

---

<a id="docs-operationsmd"></a>
## Раздел 15: `docs/operations.md`

Исходный файл: [`docs/operations.md`](../docs/operations.md)

# Ежедневные операции

## Запуск и остановка

```powershell
.\.venv\Scripts\python.exe run.py
```

В терминале проверьте строку `SQLite база: ...`, адрес LAN и QR. Остановка — `Ctrl+C`. Проверить процесс и порт можно командами `Get-NetTCPConnection -LocalPort 5000` и `Get-Process python`.

## Проверка после запуска

Откройте `/login`, войдите тестовой учётной записью, проверьте роль и назначенные фонды. Для API выполните `GET /api/funds` с Bearer-токеном. После выдачи токена сохраните секрет в менеджере секретов; повторно приложение его не покажет.

## Управление доступом

Super Admin создаёт пользователей, назначает Rights, отзывает токены и завершает browser-сессии. При подозрении на компрометацию сначала отзовите токен и все чужие сессии, затем смените пароль. Собственную учётную запись блокировать нельзя.

## Изменения базы

Не удаляйте SQLite-файл и не меняйте строки вручную во время работы. Для чистой базы выберите новый путь через `CYBRAN_DATABASE`, выполните `init-db` и создайте нового Super Admin.

---

<a id="docs-release-auditmd"></a>
## Раздел 16: `docs/release-audit.md`

Исходный файл: [`docs/release-audit.md`](../docs/release-audit.md)

# Финальный независимый аудит релиза

Дата проверки: 2026-10-08.

## Результаты

- [x] Поведение из ТЗ сохранено: роли, Rights, фонды, операции, переводы, отчёты и API-маршруты.
- [x] Запрет блокировки собственной учётной записи и защита последнего активного Super Admin подтверждены тестами.
- [x] Настройка SQLite и способов оплаты вынесена в `.env`; путь базы печатается при запуске.
- [x] Комментарии и docstring разработчика в исходниках переведены на русский; технические имена не менялись.
- [x] `.gitignore` закрывает `.env`, `.env.*` с исключением `.env.example`, SQLite, `instance/`, временные каталоги и кэши.
- [x] Runtime-зависимости перечислены в `requirements.txt`, инструменты аудита — отдельно в `requirements-audit.txt`.
- [x] Созданы русские документы по архитектуре, установке, конфигурации, базе, ролям, финансовой логике, API, тестам, deployment, операциям, backup, troubleshooting, очистке и безопасности.
- [x] Рабочие секреты, SQLite и демонстрационные пароли не отслеживаются Git; `.env.example` указывает на чистую `instance/cybran.sqlite3`, а локальный `.env` может отдельно использовать demo-базу.
- [x] Чистая конфигурация проверена на отдельном SQLite-файле через `init-db` и создание Super Admin без изменения рабочей базы.
- [x] Полный регрессионный прогон: **222 passed**.
- [x] `compileall` и `git diff --check` пройдены.
- [x] Независимый финальный аудит завершён со статусом PASS; после него удалены `tmp/`, `.pytest_cache/` и `__pycache__/`.

## Ограничения

Проверка внешней сети и HTTPS reverse proxy не выполняется внутри локального рабочего окружения. Перед production нужно отдельно проверить сертификат, Firewall, постоянный `SECRET_KEY`, резервное копирование и запуск `pip-audit`/Semgrep.

## Решение

Репозиторий готов к ручному приёмочному сценарию и подготовке deployment. Публикация в интернет возможна только после выполнения ограничений из [deployment.md](#docs-deploymentmd) и повторной проверки безопасности в целевой инфраструктуре.

---

<a id="docs-repository-cleanupmd"></a>
## Раздел 17: `docs/repository-cleanup.md`

Исходный файл: [`docs/repository-cleanup.md`](../docs/repository-cleanup.md)

# Отчёт об очистке репозитория

Проверены точки входа `run.py`, фабрика Flask, модули `auth`, `api`, `web`, `services`, `db`, шаблоны, статика, тесты и зависимости. Существующая бизнес-логика ТЗ сохранена.

## Удаляемые артефакты

После финального прогона удаляются только сгенерированные `tmp/`, `.pytest_cache/`, `__pycache__/` и старые локальные логи. В Git эти пути уже игнорируются. Рабочие `instance/*.sqlite3`, `instance/session.key` и `instance/demo-access.txt` сохраняются локально и не отслеживаются.

## Что оставлено намеренно

- `docs/MANUAL_TEST_PLAN.md`, `docs/SIMPLE_MANUAL_CHECK.md` и отчёты предыдущих приёмок нужны для ручной проверки.
- `requirements-audit.txt` содержит инструменты аудита и не смешивается с runtime-зависимостями.
- `app/static/vendor/bootstrap.min.css` — используемая локальная библиотека; её лицензионный комментарий не переводится.
- SQL-строки, endpoint, роли, имена полей и идентификаторы сохранены без перевода.

## Принцип очистки

Удаляется только доказанно сгенерированный или временный файл. Неизвестный файл не удаляется автоматически, чтобы не повредить данные или ручные материалы.

---

<a id="docs-roles-and-permissionsmd"></a>
## Раздел 18: `docs/roles-and-permissions.md`

Исходный файл: [`docs/roles-and-permissions.md`](../docs/roles-and-permissions.md)

# Роли и права

| Роль | Возможности |
|---|---|
| `Super Admin` | Полный обзор фондов и операций, пользователи, роли, Rights, архивирование, API-токены, browser-сессии, исправление истории архивных фондов, сводка и экспорт. |
| `Admin` | Назначенные Rights-фонды, доходы/расходы, перевод между двумя своими фондами, история, изменение своих операций и операций кассиров. |
| `Cashier` | Назначенные фонды, быстрый доход/расход, история и смены, отмена только своей последней операции. |
| `Investor` | Сводка и экспорт только `for_stats`; детали и история доступны только в пределах Rights. Запись операций запрещена. |

## Rights

Super Admin назначает Rights отдельными строками `user_id`/`fund_id` или всей матрицей. Для перевода Admin обязан иметь Rights на оба фонда. Отсутствие Rights даёт 403 и не раскрывает существование чужого ID. Архив фонда не убирает историю, но запрещает запись обычным ролям.

## Защита Super Admin

Нельзя заблокировать собственную учётную запись или понизить её роль. Система также не позволяет удалить последнего активного Super Admin. Смена пароля и блокировка увеличивают `auth_version`, поэтому старые сессии и API-токены перестают действовать.

## API

Cookie-сессия предназначена для HTML. REST использует только `Authorization: Bearer <token>`. Cashier и Investor не имеют API-маршрутов в таблице ТЗ и получают 403; их рабочие функции остаются в HTML-интерфейсе.

---

<a id="docs-security-auditmd"></a>
## Раздел 19: `docs/security-audit.md`

Исходный файл: [`docs/security-audit.md`](../docs/security-audit.md)

# Аудит безопасности

## Проверенное состояние

- Cookie-сессии хранят на сервере только хэш случайного идентификатора; срок — 24 часа, отзыв действует сразу.
- Пароли хранятся как PBKDF2-HMAC-SHA256 с солью; Bearer-токены — как SHA-256 и с датой истечения.
- HTML защищён CSRF; API требует Bearer и не принимает cookie как замену токену.
- RBAC и Rights проверяются в маршрутах и повторно внутри транзакций записи.
- SQL использует параметры; динамические имена таблиц и полей разрешены только из фиксированных списков.
- Security-заголовки включают CSP, HSTS при HTTPS, `X-Frame-Options`, `nosniff`, `Permissions-Policy` и `no-store` для динамических ответов.
- CSV/XLSX защищают от formula injection и потери больших целых чисел.
- Нельзя заблокировать себя или удалить последнего активного Super Admin.
- Загрузчик `.env` принимает только ожидаемые ключи конфигурации; сам файл всё равно должен быть доступен только владельцу окружения.

## Остаточные ограничения

HTTP на доверенной LAN-сети не шифрует трафик; для внешней публикации нужен HTTPS reverse proxy. Демо-база содержит простые пароли и предназначена только для локального теста. `pip-audit` и Semgrep нужно запускать в окружении, где они установлены; их отсутствие не считается успешным аудитом.

Подробные исторические результаты находятся в [SECURITY_REPORT.md](#security-reportmd) и [SECURITY_CHECKLIST.md](#security-checklistmd).

---

<a id="docs-simple-manual-checkmd"></a>
## Раздел 20: `docs/SIMPLE_MANUAL_CHECK.md`

Исходный файл: [`docs/SIMPLE_MANUAL_CHECK.md`](../docs/SIMPLE_MANUAL_CHECK.md)

# Простая ручная проверка Cybran Software

Этот сценарий написан без технических терминов. Выполняйте пункты по порядку. Если на экране получилось то, что написано в строке **Должно быть**, ставьте `[x]`. Если получилось иначе, ставьте `[!]`, запишите номер шага и сделайте снимок экрана.

Полная проверка всех ролей, API, отчётов и контрольных сумм находится в [MANUAL_TEST_PLAN.md](#docs-manual-test-planmd).

## 0. Что открыть

1. На компьютере откройте `http://127.0.0.1:5000`.
2. Для телефона отсканируйте QR-код в терминале.
3. Используйте эти локальные учётные записи:

| Кто | Логин | Пароль |
|---|---|---|
| Главный администратор | `superadmin` | `superadmin123` |
| Администратор фонда | `admin` | `admin123` |
| Кассир | `cashier` | `cashier123` |
| Инвестор | `investor` | `investor123` |

## 1. Проверить главный вход

1. Введите `superadmin` и `superadmin123`.
2. Нажмите большую красную кнопку **«Войти в систему»**.

**Должно быть:** открылся раздел **«Обзор финансов»**, слева видно меню, вверху указано **«Супер-администратор»**.

- [ ] Вход работает.
- [ ] Текст читается без увеличения масштаба браузера.
- [ ] Кнопки имеют рамку или цветной фон и выглядят как кнопки.

## 2. Проверить защиту от блокировки самого себя

1. Откройте слева **«Пользователи»**.
2. Найдите строку `superadmin` с меткой **«Это вы»**.
3. Посмотрите на действия справа.

**Должно быть:** у вашей строки есть кнопка **«Изменить»**, но нет кнопки **«Заблокировать»**. Вместо неё написано **«Собственную учётную запись нельзя блокировать»**.

4. Нажмите **«Изменить»** у `superadmin`.

**Должно быть:** сверху показано предупреждение **«Это ваша учётная запись»**, поле роли недоступно для изменения, имя и логин можно исправить, пароль можно заменить.

- [ ] Себя заблокировать нельзя.
- [ ] Свою роль Super Admin понизить нельзя.
- [ ] После возврата назад вход и меню продолжают работать.

## 3. Проверить обычную блокировку

1. В разделе **«Пользователи»** найдите `cashier`.
2. Нажмите красную кнопку **«Заблокировать»**.
3. В окне подтверждения нажмите **OK**.
4. В приватном окне браузера попробуйте войти как `cashier/cashier123`.

**Должно быть:** вход кассира запрещён, а `superadmin` продолжает работать.

5. Вернитесь в список пользователей и нажмите зелёную кнопку **«Разблокировать»**.
6. Повторите вход кассира.

**Должно быть:** вход снова работает.

- [ ] Другого пользователя можно блокировать и разблокировать.
- [ ] Цвет и текст кнопки ясно показывают действие.

## 3A. Проверить активные сессии

1. Оставьте текущий вход `superadmin` открытым.
2. Откройте приватное окно и ещё раз войдите как `superadmin`.
3. В обычном окне откройте **«Активные сессии»**.

**Должно быть:** видны две карточки входа с пользователем, IP, устройством, временем входа и автовыхода через 24 часа. У текущей карточки есть метка **«Текущая сессия»**. Никаких cookie, токенов или хэшей на странице нет.

4. У второй карточки нажмите **«Завершить сессию»**.
5. В приватном окне обновите страницу.

**Должно быть:** приватное окно вернулось на вход, обычное окно продолжает работать.

- [ ] Две сессии отображаются отдельно.
- [ ] Чужую/вторую сессию можно завершить.
- [ ] Текущая сессия не прерывается при завершении другой.
- [ ] Страница удобно читается на телефоне без горизонтальной прокрутки.

## 4. Создать два фонда

1. Слева откройте **«Все фонды»**.
2. Нажмите **«Создать фонд»**.
3. Создайте фонд `Основная касса`, тип **«Участвует в отчётности»**.
4. Так же создайте фонд `Разработка`, тип **«Участвует в отчётности»**.

**Должно быть:** появились две большие карточки фондов, на каждой видны название, баланс `0,00` и кнопка **«Открыть фонд»**.

- [ ] Оба фонда созданы.
- [ ] Карточки и кнопки не сливаются с фоном.

## 5. Выдать права

1. Откройте **«Права доступа»**.
2. Выберите `admin`, отметьте оба фонда и сохраните.
3. Выберите `cashier`, отметьте `Основная касса` и сохраните.
4. Выберите `investor`, отметьте оба фонда и сохраните.

**Должно быть:** после повторного выбора пользователя его галочки остаются на месте.

- [ ] Права сохраняются.

## 6. Проверить доход, расход и перевод

1. Выйдите и войдите как `admin/admin123`.
2. Нажмите **«Новая операция»**.
3. Добавьте доход `1000,00` в `Основная касса`, способ оплаты `Kaspi`.
4. Добавьте расход `200,00` из `Основная касса`, способ оплаты `Карта`.
5. Нажмите **«Перевод»** и переведите `300,00` из `Основная касса` в `Разработка`.

**Должно быть:** `Основная касса = 500,00`, `Разработка = 300,00`, общий остаток двух фондов = `800,00`.

- [ ] Доход добавляет деньги.
- [ ] Расход вычитает деньги.
- [ ] Перевод вычитает из одного фонда и добавляет в другой.
- [ ] У перевода явно показано направление `Основная касса → Разработка`.

## 7. Проверить кассира

1. Выйдите и войдите как `cashier/cashier123`.
2. На главном экране введите `50,00`, выберите `Наличные`, фонд `Основная касса`.
3. Нажмите большую кнопку **«Принять оплату»**.

**Должно быть:** показано сообщение об успехе, баланс основной кассы стал `550,00`.

- [ ] Главная кнопка хорошо заметна.
- [ ] Кассир не видит пользователей, права и API-токены.
- [ ] Кассир не видит межфондовый перевод.

## 8. Проверить инвестора

1. Выйдите и войдите как `investor/investor123`.
2. Откройте **«Обзор финансов»**.

**Должно быть:** общий баланс `850,00`; видны обе карточки фондов; нет кнопок создания, изменения или удаления денег; вверху есть метка **«Только просмотр»**.

- [ ] Суммы совпадают.
- [ ] Investor ничего не может изменить.

## 9. Проверить телефон

1. Откройте приложение по QR-коду.
2. Войдите как `cashier`.
3. Нажмите кнопку **«Меню»** вверху.
4. Закройте меню нажатием за его пределами.

**Должно быть:** кнопки удобно нажимать пальцем, поля не обрезаны, страница целиком не прокручивается вбок.

- [ ] Меню открывается и закрывается.
- [ ] Кнопки и поля достаточно крупные.
- [ ] Таблицы при необходимости прокручиваются внутри своего блока.

## 10. Когда проверка закончена

Проверка пройдена, если все пункты отмечены `[x]`, нет страницы с кодом 500, `superadmin` нельзя заблокировать или понизить, а итоговые балансы равны:

| Фонд | Баланс |
|---|---:|
| Основная касса | `550,00` |
| Разработка | `300,00` |
| Всего | `850,00` |

Если найден дефект, запишите: номер шага, логин, что нажали, что ожидали, что увидели и приложите снимок экрана.

---

<a id="docs-testingmd"></a>
## Раздел 21: `docs/testing.md`

Исходный файл: [`docs/testing.md`](../docs/testing.md)

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

---

<a id="docs-troubleshootingmd"></a>
## Раздел 22: `docs/troubleshooting.md`

Исходный файл: [`docs/troubleshooting.md`](../docs/troubleshooting.md)

# Устранение проблем

| Симптом | Причина | Проверка | Решение |
|---|---|---|---|
| Запуск выбирает не ту базу | Путь из `.env` или PowerShell отличается от ожидаемого | Посмотрите `SQLite база: ...` в терминале | Исправьте `.env` или `$env:CYBRAN_DATABASE`; относительный путь из `.env` считается от корня проекта. |
| `ModuleNotFoundError` | Не установлены зависимости текущего окружения | Проверьте `Test-Path .venv\Scripts\python.exe` и `-m pip check` | Создайте `.venv` и выполните `-m pip install -r requirements.txt`. |
| Не задана environment variable | `.env` отсутствует или ключ написан с ошибкой | Сравните файл с `.env.example` и проверьте `$env:CYBRAN_DATABASE` | Скопируйте `.env.example` в `.env`, задайте только поддерживаемые ключи и перезапустите процесс. |
| SQLite DB отсутствует | Каталог ещё не создавался или путь указывает в другую папку | Проверьте `Test-Path instance\cybran.sqlite3` и строку `SQLite база` | Выполните `flask --app app init-db`; каталог создаётся автоматически. |
| Permission denied при запуске или backup | У процесса нет прав на каталог базы | Проверьте права `instance/` и открытый файл | Дайте служебной учётной записи права на постоянный каталог и остановите Waitress перед копированием. |
| Порт занят | Уже запущен Waitress или другой процесс использует порт | `Get-NetTCPConnection -LocalPort 5000` | Остановите старый процесс или задайте другой `PORT`. |
| Телефон не открывает QR | Телефон и компьютер не в одной сети либо Firewall блокирует порт | Проверьте Wi-Fi, Firewall и `MOBILE_IP` | Разрешите порт только в частном профиле и укажите правильный адрес. |
| Вход не работает или сразу 429 | Неверный пароль, заблокированный пользователь или лимит попыток | Проверьте имя, статус учётной записи и подождите окно rate limit | Попросите Super Admin разблокировать пользователя или сбросить пароль; не перебирайте имена. |
| API отвечает 401 | Bearer-токен истёк, отозван или передан неверно | Проверьте заголовок `Authorization: Bearer ...`, срок и отзыв | Скопируйте секрет из окна создания токена; после отзыва создайте новый. |
| API отвечает 403 | Роль или Rights не разрешают действие | Проверьте роль и Rights на фонд(ы) | Cashier и Investor используют HTML; Admin получает Rights на каждый фонд перевода. |
| 409 при записи | Фонд архивирован или перевод повторяет существующую пару | Проверьте статус фонда и идентификаторы операции | Записывайте только в активный фонд и не повторяйте уже созданную пару. |
| Ошибка `database is locked` | Другой процесс держит SQLite-транзакцию | Убедитесь, что не запущены два Waitress и не идёт backup | Оставьте один процесс, дождитесь завершения backup и повторите операцию. |
| CSV/XLSX не скачивается | Неверный формат, фильтр или отсутствует `openpyxl` | Проверьте `format=csv|xlsx`, ответ API и `pip check` | Повторите запрос с поддерживаемым форматом и установите `requirements.txt`. |
| `%TEMP%` запрещён для pytest | Системный временный каталог недоступен | Выполните `New-Item -ItemType Directory -Force tmp` и используйте `--basetemp=tmp/pytest_release` | Используйте проектный каталог для временных файлов. |
| Сломались cookie после deploy | Изменился `SECRET_KEY` или неверны HTTPS/proxy-настройки | Проверьте постоянство `SECRET_KEY`, `COOKIE_SECURE` и число proxy-hop | Верните тот же ключ, включите HTTPS и задайте корректный `TRUSTED_PROXY_HOPS`; затем войдите заново. |

При неизвестной ошибке сохраните код ответа, путь, время и безопасный фрагмент лога без токенов и паролей. Не прикладывайте SQLite или `session.key` к публичному отчёту.

---

<a id="docs-verificationmd"></a>
## Раздел 23: `docs/VERIFICATION.md`

Исходный файл: [`docs/VERIFICATION.md`](../docs/VERIFICATION.md)

# Финальная приёмка — 2026-10-08

Приложение реализовано и проверено по всем 10 страницам «ТЗ для Бубелиса Йонаса.pdf» и пользовательской цели. Перед завершением исходный PDF открыт повторно; весь извлеченный текст совпал с первоначально прочитанным. SHA-256 исходника: `4795a1ad096dd4815d6adb5cdc8d7b6315dce07e2f08025b5e3ad698bf04ebf9`.

## Автоматические проверки

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q --basetemp=tmp/pytest_full_security_final2
# 222 теста пройдено за 96.18 с при свежем повторном аудите PDF-ТЗ после исправлений лимитов, proxy, архивов, сессий и конфигурации проекта
.\.venv\Scripts\python.exe -m compileall -q app tests run.py
.\.venv\Scripts\python.exe -m pip check
# Конфликты зависимостей не обнаружены.
git diff --check
```

Все проверки завершились успешно. Набор покрывает четыре роли, все 16 обязательных method/path API, CSRF, server-side сессии, их одиночный/массовый отзыв и абсолютное 24-часовое завершение, login throttling, блокировку, Rights/IDOR, авторство при исправлении, атомарность переводов, фильтры, архив, KPI, отчеты, CSV/XLSX и защиту от формул в экспортах. Для проверки rollback устанавливались реальные SQLite-триггеры с ошибкой на второй вставке, обновлении или удалении пары.

Отдельно на новой пустой SQLite выполнены CLI `init-db` и `create-superadmin` с последующим настоящим входом через форму и открытием dashboard. Рабочая и демонстрационная базы прошли `PRAGMA integrity_check` и `PRAGMA foreign_key_check`. Демо запущено через Waitress на `http://127.0.0.1:5000`; начальная рабочая база остается пустой. Секреты и демонстрационная база исключены из Git.

## Браузер

Проверено через Codex Browser на живом приложении:

- Вход/выход Super Admin, дашборд с KPI, графиком динамики и распределением средств, переходы к фондам и переводу.
- Desktop и viewport 390×844: дашборд, меню, список фондов, форма перевода, экран кассира; `scrollWidth == clientWidth`, без горизонтального переполнения страницы. Таблицы имеют собственную горизонтальную прокрутку.
- Cashier: прием тестовой суммы `12,34` через настоящую форму; успешный alert и запись `+12,34` с автором и способом оплаты в истории. У кассира нет управления пользователями и межфондовых переводов.
- Investor: режим чтения, три отчетных фонда в сводке, ссылки детализации согласно Rights; прямой переход к `no_stats` возвращает страницу 403; ссылка Excel инициирует загрузку файла.
- Консоль браузера не показала ошибок в проверенных сценариях. Временный viewport возвращен к исходному размеру.
- Super Admin: открыта страница «Активные сессии» с текущим входом, IP, устройством, временем входа/активности/автовыхода и действиями завершения. Секрет cookie и его hash в интерфейс не выводятся.

Frontend-агент дополнительно проверил рендер защищённых HTML-путей, компиляцию всех 19 Jinja-шаблонов, изменение по любому ID пары, CSRF-форму перевода с пустым необязательным pay_type и однократный показ токена. Остальные ролевые формы и серверные запреты проверяются HTTP-интеграционными тестами; утверждение о ручном нажатии каждой кнопки в браузере не делается.

## Независимый аудит

Отдельный read-only субагент повторно изучил PDF, решения D01–D12, схему, backend, UI и тесты. Четыре найденных дефекта исправлены:

1. XML-недопустимые символы в тексте могли прерывать XLSX-экспорт — теперь отклоняются до сохранения.
2. Длинные дробные суммы могли округляться контекстом Decimal — дробные minor units проверяются по точным цифрам до арифметики.
3. Не-ASCII CSRF-токен вызывал исключение — теперь возвращается 400.
4. Переполнение даты при переводе крайнего ISO-времени в UTC вызывало исключение — теперь возвращается 400.

Дополнительно проверены слишком длинные ID, некорректный Unicode пароля, максимальный SQLite INTEGER и точные суммы с хвостовыми нулями. Аудитор независимо перепроверил ранние исправления: **14 passed in 3.38s**. После добавления защиты Super Admin от самоблокировки/самопонижения, строгой проверки HTML-флага блокировки и явной валидации API-пароля полный набор проверен снова: **197 passed in 38.03s**.

Запущенное приложение дополнительно проверено реальными HTTP-запросами: попытка Super Admin заблокировать себя и попытка понизить собственную роль вернули `409`, после каждого запроса в SQLite сохранилось `role='Super Admin', is_active=1`. В браузере подтверждены метка «Это вы», отсутствие кнопки самоблокировки, заблокированное поле собственной роли и увеличенные кнопки/поля. На порту 5000 оставлен один актуальный экземпляр сервера.

Отдельный read-only аудитор повторно проверил итоговый код, rollback, HTML и конкурентный сценарий с устаревшим объектом пользователя: **10 целевых тестов прошли, незакрытых замечаний нет**.

После security-аудита добавлены серверный реестр сессий, завершение сессий Super Admin, 24-часовой абсолютный срок, bounded login throttling, dummy password path, 30-дневные API-токены, отзыв токенов при сбросе пароля, CSP, унификация 404 для чужих финансовых объектов, trusted-proxy client-IP, request-time authorization recheck, retention cleanup, запрет нижним ролям менять архивную историю, project `.env` и настраиваемые способы оплаты. Свежий полный suite при повторной сверке PDF-ТЗ: **222 passed in 96.18s**; auth/session focused suite: **68 passed**, management/integrity: **44 passed**, limiter-focused auth: **60 passed**, config: **5 passed**. `pip-audit` и Semgrep на этом хосте не получили валидный advisory/findings result из-за сетевых/config ограничений; Bandit оставляет только явно документированный LAN bind `0.0.0.0`. Полные доказательства и оставшийся риск HTTP/LAN описаны в `SECURITY_REPORT.md`.

## Мобильное подключение

`run.py` слушает `0.0.0.0`, определяет приватные IPv4-адреса и печатает в терминале ссылку и сканируемый QR-код. Проверены ответы `200 OK` по `http://192.168.6.139:5000/login` и `http://192.168.137.1:5000/login`; `netstat` подтверждает прослушивание `0.0.0.0:5000`. Правило Windows Firewall `Cybran Software Mobile` ограничено TCP-портом 5000, профилями Domain/Private и двумя локальными подсетями; доступ из интернета не открывался.

Все строки `REQUIREMENTS_CHECKLIST.md` сопоставлены с реализацией и проверками. Разрешение неоднозначностей ТЗ изложено в `DECISIONS.md`; новые бизнес-модули, роли и финансовые правила не добавлялись.

---
