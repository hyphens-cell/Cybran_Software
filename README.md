# Cybran Software

CRM учёта финансов по фондам. Python + Flask + SQLite + Jinja2 + Bootstrap; серверные страницы и REST API. Требования сверяются с исходным PDF в [REQUIREMENTS_CHECKLIST.md](REQUIREMENTS_CHECKLIST.md), решения по противоречиям — в [docs/DECISIONS.md](docs/DECISIONS.md).

## Запуск в Windows PowerShell

Нужен Python 3.12+. Зависимости приложения устанавливаются в виртуальное окружение проекта.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app init-db
.\.venv\Scripts\python.exe -m flask --app app create-superadmin
.\.venv\Scripts\python.exe run.py
```

После запуска терминал показывает адрес для телефона и QR-код. Телефон и компьютер должны находиться в одной локальной сети; наведите камеру на QR-код. На этом компьютере текущий адрес: `http://192.168.6.139:5000`. Если телефон подключен к мобильной точке Windows, можно выбрать ее адрес через `$env:MOBILE_IP = '192.168.137.1'` перед запуском. Команда создания Super Admin запрашивает логин и пароль. В исходниках нет предустановленного пароля. SQLite автоматически создаётся при первом запуске; повторный `init-db` сохраняет данные. В этом рабочем окружении `.venv` уже подготовлено, поэтому первые два шага повторять не требуется.

На текущем компьютере создано правило Windows Firewall `Cybran Software Mobile`: TCP-порт 5000 разрешен только для локальной сети `192.168.0.0/19` и мобильной точки `192.168.137.0/24`, только в профилях Domain/Private. Удалить правило после окончания работы можно из PowerShell администратора: `netsh advfirewall firewall delete rule name="Cybran Software Mobile"`.

Приложение запускается через Waitress без debug/reloader. Для мобильного доступа оно слушает локальные интерфейсы (`0.0.0.0`); `HOST=127.0.0.1` возвращает режим «только этот компьютер», а `PORT` меняет порт. Это подключение предназначено для доверенной локальной сети, не для публикации в интернете. Для публичного размещения используйте HTTPS reverse proxy, установите `COOKIE_SECURE=1` и собственный `SECRET_KEY`. Не используйте Flask debug в публичном окружении.

## Демонстрационная база

```powershell
$env:CYBRAN_DATABASE = Join-Path (Get-Location) 'instance\demo.sqlite3'
.\.venv\Scripts\python.exe -m flask --app app seed-demo
.\.venv\Scripts\python.exe run.py
```

`seed-demo` работает только с пустой базой и создаёт четыре роли, четыре фонда, пример истории и перевод. Простые пароли для локальной демонстрации сохраняются в `instance/demo-access.txt`; использовать их в рабочей базе нельзя. Это демонстрационные операции. Для собственной чистой базы уберите переменную `CYBRAN_DATABASE`, выполните `create-superadmin` и запустите сервер заново. Демоданные автоматически при запуске не добавляются.

## Работа с системой

- **Super Admin:** сводка, все фонды/операции, пользователи, роли, блокировка, сброс пароля, матрица прав, API-токены и настройки участия фондов в отчётности.
- **Admin:** баланс и история фондов из Rights, доходы/расходы, перевод между двумя своими фондами, исправление своих операций и операций кассиров.
- **Cashier:** быстрая форма оплаты, расход, история доступных фондов и смен по дням, отмена только своей последней операции.
- **Investor:** сводка всех `for_stats`, CSV/Excel за период; отдельная история доступна для `for_stats` с Rights. `no_stats` и недоступные стороны переводов скрыты.

Сумма в HTML-форме вводится в основных единицах с двумя десятичными знаками (например, `1250,50`); в БД и API это `125050` minor units. Валюту система не назначает. Время операций хранится в UTC, границы дат включают весь выбранный день. Баланс — текущий; оборот/расход/чистый поток — за выбранный период; месячные показатели — за текущий месяц. Отрицательные остатки разрешены, так как запрета в ТЗ нет.

Перевод — две связанные записи `inter-transaction`, одна уменьшает источник, другая увеличивает получателя. В UI/экспорте это одна операция. Изменение/удаление любого ID пары меняет обе записи атомарно. Переводы не включаются во внешние доходы/расходы. Архив фонда сохраняет историю и остатки, запрещает новые операции; Super Admin может исправлять прошлые записи.

## REST API

Все обязательные endpoints сохранены. Токен генерируется только в интерфейсе Super Admin → API-токены, показывается один раз и хранится в БД как SHA-256. Каждый запрос передаёт `Authorization: Bearer <128-символьный токен>`; cookie-сессия для API не подходит. Владелец определяет роль и Rights; отзыв токена и блокировка владельца действуют немедленно.

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

## Проверка и устройство

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp=tmp/pytest
.\.venv\Scripts\python.exe -m compileall -q app tests run.py
.\.venv\Scripts\python.exe -m flask --app app routes
```

Тесты используют отдельные временные SQLite-файлы и не меняют рабочую базу. Проверяются роли, IDOR, CSRF, токены, финансовые балансы, откат второй записи перевода, отчётность и экспорты.

`app/db.py` — схема и транзакции; `services.py` — бизнес-правила; `auth.py` — аутентификация; `api.py` — REST; `web.py` — HTML; `templates/` и `static/` — интерфейс; `tests/` — интеграционная проверка. Bootstrap хранится локально, внешних CDN приложение не требует. Логотип предоставлен пользователем.

Рабочая база и ключ сессий находятся в `instance/` (исключено из Git). Для резервной копии остановите сервер и скопируйте SQLite вместе с ключом сессий либо используйте SQLite backup API. Пароль хранится как PBKDF2-HMAC-SHA256 с солью, Bearer-токен — SHA-256. В CSV защищены пользовательские формулы; в XLSX текст сохраняется текстом, целые числа свыше 15 цифр — строками без потери точности Excel.
