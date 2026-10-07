import os
import secrets
import sqlite3
from pathlib import Path

import click
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from .db import atomic, close_db, init_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.environ.get('CYBRAN_DATABASE', str(Path(app.instance_path) / 'cybran.sqlite3')),
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        CSRF_ENABLED=True, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE') == '1', MAX_CONTENT_LENGTH=1024*1024,
    )
    if test_config:
        app.config.update(test_config)
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
        return {'current_user': getattr(g, 'user', None), 'csrf_token': auth.csrf_token}

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
        if not request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.cli.command('init-db')
    def initialize():
        init_db()
        click.echo('SQLite database initialized.')

    @app.cli.command('create-superadmin')
    @click.option('--username', prompt=True)
    @click.option('--fullname', default='Супер-администратор', show_default=True)
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
    def create_superadmin(username, fullname, password):
        from .services import password_hash, text_value
        with atomic() as db:
            db.execute('INSERT INTO Users(username,fullname,password_hash,role) VALUES(?,?,?,?)',
                       (text_value(username, 'Логин', 50), text_value(fullname, 'Имя', 150),
                        password_hash(password), 'Super Admin'))
        click.echo('Super Admin created.')

    @app.cli.command('seed-demo')
    def demo():
        from .demo import seed_demo
        seed_demo()

    return app
