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
