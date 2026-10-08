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
