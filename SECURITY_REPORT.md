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
