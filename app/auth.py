"""Cookie-сессии HTML и независимая Bearer-аутентификация REST API."""
import hashlib
import secrets
from datetime import datetime, timezone
from functools import wraps

from flask import Blueprint, abort, current_app, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import atomic, get_db

bp = Blueprint('auth', __name__)
SESSION_TOKEN_BYTES = 32
_DUMMY_PASSWORD_HASH = None


def _utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _iso(value):
    return value.isoformat(timespec='seconds')


def _session_hash(value):
    if not isinstance(value, str):
        return None
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def _client_details():
    return (request.remote_addr or '')[:45], (request.user_agent.string or '')[:300]


def _dummy_password_hash():
    global _DUMMY_PASSWORD_HASH
    if _DUMMY_PASSWORD_HASH is None:
        _DUMMY_PASSWORD_HASH = generate_password_hash(
            secrets.token_urlsafe(32), method='pbkdf2:sha256:600000')
    return _DUMMY_PASSWORD_HASH


def _login_rate_keys(username=None):
    ip_address = (request.remote_addr or 'unknown')[:45]
    per_ip = hashlib.sha256(f'ip\0{ip_address}'.encode('utf-8')).hexdigest()
    keys = [(per_ip, current_app.config['LOGIN_IP_ATTEMPTS'])]
    if username is not None:
        account_name = username.strip().casefold()[:50]
        account = hashlib.sha256(f'account\0{account_name}'.encode('utf-8')).hexdigest()
        pair = hashlib.sha256(f'account\0{ip_address}\0{account_name}'.encode('utf-8')).hexdigest()
        keys[:0] = [(account, current_app.config['LOGIN_ACCOUNT_GLOBAL_ATTEMPTS']),
                    (pair, current_app.config['LOGIN_ACCOUNT_ATTEMPTS'])]
    return keys


def _reserve_login_attempt(username=None):
    now = _utc_now()
    window_start = now - current_app.config['LOGIN_RATE_WINDOW']
    blocked_for = 0
    with atomic():
        db = get_db()
        db.execute('DELETE FROM LoginAttempts WHERE window_started_at<=?', (_iso(window_start),))
        keys = _login_rate_keys(username)
        # Сначала проверяем общий лимит клиента и только потом создаём
        # состояние для логина. Заблокированный клиент не сможет раздувать
        # LoginAttempts перебором новых имён.
        ip_key, ip_limit = keys[-1]
        ip_row = db.execute('SELECT attempts,window_started_at FROM LoginAttempts WHERE key_hash=?',
                            (ip_key,)).fetchone()
        if ip_row and datetime.fromisoformat(ip_row['window_started_at']) > window_start \
                and ip_row['attempts'] >= ip_limit:
            started_at = datetime.fromisoformat(ip_row['window_started_at'])
            return int((started_at + current_app.config['LOGIN_RATE_WINDOW'] - now).total_seconds()) + 1
        for key_hash, limit in keys[:-1]:
            row = get_db().execute('SELECT attempts,window_started_at FROM LoginAttempts WHERE key_hash=?',
                                   (key_hash,)).fetchone()
            if row is None or datetime.fromisoformat(row['window_started_at']) <= window_start:
                attempts, started_at = 1, now
                get_db().execute('''INSERT INTO LoginAttempts(key_hash,attempts,window_started_at) VALUES(?,?,?)
                    ON CONFLICT(key_hash) DO UPDATE SET attempts=excluded.attempts,
                    window_started_at=excluded.window_started_at''', (key_hash, attempts, _iso(started_at)))
            else:
                attempts = row['attempts'] + 1
                started_at = datetime.fromisoformat(row['window_started_at'])
                get_db().execute('UPDATE LoginAttempts SET attempts=? WHERE key_hash=?', (attempts, key_hash))
            if attempts > limit:
                blocked_for = max(blocked_for, int((started_at + current_app.config['LOGIN_RATE_WINDOW'] - now).total_seconds()) + 1)
        # Общую строку клиента обновляем последней: заблокированный клиент не
        # получает новые строки учётных записей, но достигший лимита запрос
        # всё равно учитывается.
        row = db.execute('SELECT attempts,window_started_at FROM LoginAttempts WHERE key_hash=?', (ip_key,)).fetchone()
        if row is None or datetime.fromisoformat(row['window_started_at']) <= window_start:
            attempts, started_at = 1, now
            db.execute('''INSERT INTO LoginAttempts(key_hash,attempts,window_started_at) VALUES(?,?,?)
                ON CONFLICT(key_hash) DO UPDATE SET attempts=excluded.attempts,
                window_started_at=excluded.window_started_at''', (ip_key, attempts, _iso(started_at)))
        else:
            attempts = row['attempts'] + 1
            started_at = datetime.fromisoformat(row['window_started_at'])
            db.execute('UPDATE LoginAttempts SET attempts=? WHERE key_hash=?', (attempts, ip_key))
        if attempts > ip_limit:
            blocked_for = max(blocked_for, int((started_at + current_app.config['LOGIN_RATE_WINDOW'] - now).total_seconds()) + 1)
        max_rows = max(100, int(current_app.config['LOGIN_ATTEMPT_MAX_ROWS']))
        row_count = db.execute('SELECT COUNT(*) AS count FROM LoginAttempts').fetchone()['count']
        if row_count > max_rows:
            db.execute('''DELETE FROM LoginAttempts WHERE key_hash IN
                (SELECT key_hash FROM LoginAttempts ORDER BY window_started_at ASC LIMIT ?)''',
                       (row_count - max_rows,))
    return blocked_for


def _clear_account_login_attempts(username):
    account_keys = [key_hash for key_hash, _limit in _login_rate_keys(username)[:-1]]
    with atomic():
        get_db().execute('DELETE FROM LoginAttempts WHERE key_hash IN (?,?)', tuple(account_keys))


def _create_web_session(user):
    """Создать отзывную браузерную сессию с абсолютным сроком жизни."""
    token = secrets.token_urlsafe(SESSION_TOKEN_BYTES)
    now = _utc_now()
    expires = now + current_app.config['WEB_SESSION_LIFETIME']
    ip_address, user_agent = _client_details()
    cursor = get_db().execute('''INSERT INTO WebSessions
        (session_hash,user_id,auth_version,created_at,last_seen_at,expires_at,ip_address,user_agent)
        VALUES(?,?,?,?,?,?,?,?)''',
        (_session_hash(token), user['id'], user['auth_version'], _iso(now), _iso(now),
         _iso(expires), ip_address, user_agent))
    return token, cursor.lastrowid


def csrf_token():
    if '_csrf' not in session:
        session['_csrf'] = secrets.token_urlsafe(32)
    return session['_csrf']


def load_user():
    g.user = None
    g.web_session_id = None
    g.api_token_id = None
    g.session_end_reason = None
    now = _utc_now()
    if request.path.startswith('/api/'):
        _prune_web_sessions(now)
        return
    if session.get('user_id'):
        session_hash = _session_hash(session.get('web_session_token'))
        now_iso = _iso(now)
        row = get_db().execute('''SELECT u.*,s.id AS web_session_id,s.auth_version AS session_auth_version,
            s.expires_at AS session_expires_at,s.revoked_at AS session_revoked_at
            FROM Users u JOIN WebSessions s ON s.user_id=u.id
            WHERE u.id=? AND s.session_hash=?''',
            (session['user_id'], session_hash)).fetchone() if session_hash else None
        if (row and row['session_revoked_at'] is None and row['session_expires_at'] > now_iso
                and row['is_active'] and session.get('auth_version') == row['auth_version']
                and row['session_auth_version'] == row['auth_version']):
            g.user = {key: row[key] for key in ('id','username','fullname','password_hash','role','is_active','auth_version')}
            g.web_session_id = row['web_session_id']
            ip_address, user_agent = _client_details()
            get_db().execute('''UPDATE WebSessions SET last_seen_at=?,ip_address=?,user_agent=?
                WHERE id=?''', (now_iso, ip_address, user_agent, g.web_session_id))
        else:
            if row and row['session_expires_at'] <= now_iso:
                g.session_end_reason = 'expired'
            elif row:
                g.session_end_reason = '1'
            session.clear()
    if request.method in ('POST', 'PUT', 'PATCH', 'DELETE') and current_app.config['CSRF_ENABLED']:
        supplied = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token', '')
        expected = session.get('_csrf', '')
        if not expected or not isinstance(supplied, str) or not supplied.isascii() or not secrets.compare_digest(expected, supplied):
            abort(400, description='Сессия формы истекла. Обновите страницу и повторите действие.')
    _prune_web_sessions(now)


def _prune_web_sessions(now=None):
    now = now or _utc_now()
    retention_cutoff = _iso(now - current_app.config['WEB_SESSION_RETENTION'])
    get_db().execute('''DELETE FROM WebSessions
        WHERE (revoked_at IS NULL AND expires_at<=?)
           OR (revoked_at IS NOT NULL AND revoked_at<=?)''',
                     (_iso(now), retention_cutoff))


def login_required(view):
    """Разрешить HTML-маршрут только действующей серверной сессии."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', ended=g.session_end_reason)) if g.session_end_reason else redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*roles):
    """Добавить проверку роли поверх обязательной браузерной сессии."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if g.user['role'] not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


def authenticate_api():
    """Проверить Bearer-токен и установить активного владельца API-запроса."""
    auth = request.headers.get('Authorization', '').split()
    if len(auth) != 2 or auth[0].lower() != 'bearer' or len(auth[1]) != 128:
        abort(401, description='Требуется действующий Bearer API token.')
    # Открытый токен сразу превращается в SHA-256: в БД и журналах не хранится
    # секрет, который пользователь передал в заголовке запроса.
    digest = hashlib.sha256(auth[1].encode('utf-8')).hexdigest()
    # Одновременно проверяем отзыв, срок действия и активность владельца, чтобы
    # заблокированный пользователь или отозванный токен потерял доступ немедленно.
    row = get_db().execute('''SELECT u.*,t.id AS api_token_id FROM Users u JOIN ApiTokens t ON t.user_id=u.id
        WHERE t.token=? AND t.active=1 AND t.expires_at>? AND u.is_active=1''',
        (digest, _iso(_utc_now()))).fetchone()
    if row is None:
        abort(401, description='Токен недействителен или отозван.')
    g.api_token_id = row['api_token_id']
    g.user = dict(row)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    notice = {
        '1': 'Сессия завершена. Для продолжения войдите снова.',
        'all': 'Все активные сессии завершены.',
        'expired': 'Прошло 24 часа с момента входа. Войдите снова.',
    }.get(request.args.get('ended'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        row = get_db().execute('SELECT * FROM Users WHERE username=?', (username,)).fetchone()
        retry_after = _reserve_login_attempt(username)
        if retry_after:
            response = render_template('auth/login.html', error='Слишком много попыток входа. Подождите несколько минут.', notice=None)
            return response, 429, {'Retry-After': str(retry_after)}
        password_ok = check_password_hash(
            row['password_hash'] if row and row['is_active'] else _dummy_password_hash(), password)
        if row and row['is_active'] and password_ok:
            with atomic():
                token, _session_id = _create_web_session(row)
            _clear_account_login_attempts(username)
            session.clear()
            session.permanent = True
            session.update(user_id=row['id'], auth_version=row['auth_version'], web_session_token=token)
            csrf_token()
            return redirect(url_for('web.index'))
        error = 'Неверный логин или пароль, либо пользователь заблокирован.'
    return render_template('auth/login.html', error=error, notice=notice), (401 if error else 200)


@bp.post('/logout')
@login_required
def logout():
    now = _iso(_utc_now())
    if g.web_session_id is not None:
        with atomic():
            get_db().execute('''UPDATE WebSessions SET revoked_at=?,revoked_by=?
                WHERE id=? AND revoked_at IS NULL''', (now, g.user['id'], g.web_session_id))
    session.clear()
    return redirect(url_for('auth.login'))
