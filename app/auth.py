"""Cookie sessions for HTML and independent Bearer authentication for REST."""
import hashlib
import secrets
from functools import wraps

from flask import Blueprint, abort, current_app, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db

bp = Blueprint('auth', __name__)


def csrf_token():
    if '_csrf' not in session:
        session['_csrf'] = secrets.token_urlsafe(32)
    return session['_csrf']


def load_user():
    g.user = None
    if request.path.startswith('/api/'):
        return
    if session.get('user_id'):
        row = get_db().execute('SELECT * FROM Users WHERE id=?', (session['user_id'],)).fetchone()
        if row and row['is_active'] and session.get('auth_version') == row['auth_version']:
            g.user = dict(row)
        else:
            session.clear()
    if request.method in ('POST', 'PUT', 'PATCH', 'DELETE') and current_app.config['CSRF_ENABLED']:
        supplied = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token', '')
        expected = session.get('_csrf', '')
        if not expected or not isinstance(supplied, str) or not supplied.isascii() or not secrets.compare_digest(expected, supplied):
            abort(400, description='Сессия формы истекла. Обновите страницу и повторите действие.')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*roles):
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
    auth = request.headers.get('Authorization', '').split()
    if len(auth) != 2 or auth[0].lower() != 'bearer' or len(auth[1]) != 128:
        abort(401, description='Требуется действующий Bearer API token.')
    digest = hashlib.sha256(auth[1].encode('utf-8')).hexdigest()
    row = get_db().execute('''SELECT u.* FROM Users u JOIN ApiTokens t ON t.user_id=u.id
        WHERE t.token=? AND t.active=1 AND u.is_active=1''', (digest,)).fetchone()
    if row is None:
        abort(401, description='Токен недействителен или отозван.')
    g.user = dict(row)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        row = get_db().execute('SELECT * FROM Users WHERE username=?', (username,)).fetchone()
        if row and row['is_active'] and check_password_hash(row['password_hash'], password):
            session.clear()
            session.update(user_id=row['id'], auth_version=row['auth_version'])
            csrf_token()
            return redirect(url_for('web.index'))
        error = 'Неверный логин или пароль, либо пользователь заблокирован.'
    return render_template('auth/login.html', error=error), (401 if error else 200)


@bp.post('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
