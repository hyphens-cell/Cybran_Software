import os
import secrets
import sqlite3
from datetime import timedelta
from pathlib import Path

import click
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import DEFAULT_PAYMENT_METHODS, load_project_env, parse_payment_methods
from .db import atomic, close_db, init_db

load_project_env()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.environ.get('CYBRAN_DATABASE', str(Path(app.instance_path) / 'cybran.sqlite3')),
        PAYMENT_METHODS=os.environ.get('PAYMENT_METHODS', ','.join(DEFAULT_PAYMENT_METHODS)),
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        CSRF_ENABLED=True, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE') == '1', MAX_CONTENT_LENGTH=1024*1024,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=24), SESSION_REFRESH_EACH_REQUEST=False,
        WEB_SESSION_LIFETIME=timedelta(hours=24),
        WEB_SESSION_RETENTION=timedelta(days=30),
        LOGIN_RATE_WINDOW=timedelta(minutes=5), LOGIN_ACCOUNT_ATTEMPTS=5,
        LOGIN_ACCOUNT_GLOBAL_ATTEMPTS=20, LOGIN_IP_ATTEMPTS=30, LOGIN_ATTEMPT_MAX_ROWS=10000,
        API_TOKEN_LIFETIME=timedelta(days=30),
        TRUSTED_PROXY_HOPS=int(os.environ.get('TRUSTED_PROXY_HOPS', '0')),
    )
    if test_config:
        app.config.update(test_config)
    app.config['PAYMENT_METHODS'] = parse_payment_methods(app.config.get('PAYMENT_METHODS'))
    trusted_proxy_hops = max(0, int(app.config.get('TRUSTED_PROXY_HOPS', 0)))
    if trusted_proxy_hops:
        # Доверяем forwarded-заголовкам только при явно заданном количестве
        # контролируемых proxy-hop. Сетевой контур должен закрывать прямой
        # доступ клиентов к backend в обход обратного прокси.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=trusted_proxy_hops,
                                x_proto=trusted_proxy_hops)
    app.config.setdefault('DEMO_MODE', Path(app.config['DATABASE']).name.casefold() == 'demo.sqlite3')
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if not app.config['SECRET_KEY']:
        secret_path = Path(app.instance_path) / 'session.key'
        try:
            with secret_path.open('x', encoding='ascii') as stream:
                stream.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        app.config['SECRET_KEY'] = secret_path.read_text(encoding='ascii').strip()
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    from . import auth, api, web
    from .services import DomainError
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(web.bp)
    app.before_request(auth.load_user)

    @app.context_processor
    def template_context():
        from flask import g
        return {'current_user': getattr(g, 'user', None), 'csrf_token': auth.csrf_token,
                'demo_mode': app.config['DEMO_MODE'], 'payment_methods': app.config['PAYMENT_METHODS']}

    @app.template_filter('money')
    def money(value):
        value = int(value or 0)
        sign = '−' if value < 0 else ''
        major, minor = divmod(abs(value), 100)
        return f'{sign}{major:,}'.replace(',', ' ') + f',{minor:02d}'

    @app.errorhandler(DomainError)
    def domain_error(error):
        return error_response(error.status, str(error))

    @app.errorhandler(HTTPException)
    def http_error(error):
        messages = {403: 'Недостаточно прав для этого действия.', 404: 'Страница или запись не найдена.',
                    405: 'Метод запроса не поддерживается.'}
        return error_response(error.code, messages.get(error.code, error.description))

    @app.errorhandler(sqlite3.IntegrityError)
    def integrity_error(_error):
        return error_response(409, 'Изменение нарушает целостность данных или запись уже существует.')

    @app.errorhandler(500)
    def internal_error(_error):
        return error_response(500, 'Не удалось выполнить действие. Изменения отменены.')

    def error_response(code, message):
        if request.path.startswith('/api/'):
            response = jsonify(error=message)
            if code == 401:
                response.headers['WWW-Authenticate'] = 'Bearer'
            return response, code
        return render_template('error.html', code=code, message=message), code

    @app.after_request
    def secure_response(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'none'; form-action 'self'")
        response.headers['Permissions-Policy'] = 'camera=(), geolocation=(), microphone=()'
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        if not request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.cli.command('init-db')
    def initialize():
        """Идемпотентно создать таблицы SQLite, не очищая рабочие данные."""
        init_db()
        click.echo('SQLite база инициализирована.')

    @app.cli.command('create-superadmin')
    @click.option('--username', prompt=True)
    @click.option('--fullname', default='Супер-администратор', show_default=True)
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
    def create_superadmin(username, fullname, password):
        """Создать первого активного Super Admin с хешем пароля."""
        from .services import password_hash, text_value
        with atomic() as db:
            db.execute('INSERT INTO Users(username,fullname,password_hash,role) VALUES(?,?,?,?)',
                       (text_value(username, 'Логин', 50), text_value(fullname, 'Имя', 150),
                        password_hash(password), 'Super Admin'))
        click.echo('Super Admin создан.')

    @app.cli.command('seed-demo')
    def demo():
        from .demo import seed_demo
        seed_demo()

    return app
