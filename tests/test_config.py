import os
from pathlib import Path

from app import create_app
from app.config import load_project_env, parse_payment_methods


def test_project_env_resolves_database_relative_to_project_file(tmp_path, monkeypatch):
    env_file = tmp_path / '.env'
    env_file.write_text('CYBRAN_DATABASE=instance/demo.sqlite3\nHOST="127.0.0.1"\n', encoding='utf-8')
    monkeypatch.delenv('CYBRAN_DATABASE', raising=False)
    monkeypatch.delenv('HOST', raising=False)

    assert load_project_env(env_file) == env_file
    assert Path(os.environ['CYBRAN_DATABASE']) == (tmp_path / 'instance/demo.sqlite3').resolve()
    assert os.environ['HOST'] == '127.0.0.1'


def test_shell_environment_wins_over_project_env(tmp_path, monkeypatch):
    env_file = tmp_path / '.env'
    env_file.write_text('CYBRAN_DATABASE=instance/demo.sqlite3\nHOST=0.0.0.0\n', encoding='utf-8')
    monkeypatch.setenv('CYBRAN_DATABASE', 'external.sqlite3')
    monkeypatch.setenv('HOST', '127.0.0.1')

    load_project_env(env_file)
    assert os.environ['CYBRAN_DATABASE'] == 'external.sqlite3'
    assert os.environ['HOST'] == '127.0.0.1'


def test_project_env_ignores_unknown_keys(tmp_path, monkeypatch):
    env_file = tmp_path / '.env'
    env_file.write_text('UNEXPECTED_SETTING=ignored\nHOST=127.0.0.1\n', encoding='utf-8')
    monkeypatch.delenv('UNEXPECTED_SETTING', raising=False)
    monkeypatch.delenv('HOST', raising=False)

    load_project_env(env_file)

    assert 'UNEXPECTED_SETTING' not in os.environ
    assert os.environ['HOST'] == '127.0.0.1'


def test_payment_methods_are_normalized_and_have_a_fallback():
    assert parse_payment_methods('Наличные, Kaspi, Наличные') == ('Наличные', 'Kaspi')
    assert parse_payment_methods('') == ('Наличные', 'Kaspi', 'Карта')


def test_create_app_applies_payment_methods_to_runtime_config(tmp_path):
    app = create_app({'TESTING': True, 'SECRET_KEY': 'test-secret',
                      'DATABASE': str(tmp_path / 'config.sqlite3'),
                      'PAYMENT_METHODS': 'QR, Карта, QR'})

    assert app.config['PAYMENT_METHODS'] == ('QR', 'Карта')
