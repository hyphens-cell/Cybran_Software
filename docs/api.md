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
