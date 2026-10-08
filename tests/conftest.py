"""Изолированные SQLite-фикстуры и настоящая HTTP-аутентификация для приёмочных тестов."""
import hashlib

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.db import get_db


PASSWORD = "CorrectPassword-123"
ROLES = {"root": "Super Admin", "admin": "Admin", "other_admin": "Admin",
         "cashier": "Cashier", "other_cashier": "Cashier", "investor": "Investor"}


@pytest.fixture(scope="session")
def seed_password_hash():
    return generate_password_hash(PASSWORD, method="pbkdf2:sha256:600000")


@pytest.fixture
def app(tmp_path, seed_password_hash):
    app = create_app({"TESTING": True, "SECRET_KEY": "test-only-session-secret",
                      "DATABASE": str(tmp_path / "test.sqlite3"), "CSRF_ENABLED": True})
    with app.app_context():
        db = get_db()
        for user_id, (username, role) in enumerate(ROLES.items(), 1):
            db.execute("INSERT INTO Users(id,username,fullname,password_hash,role) VALUES(?,?,?,?,?)",
                       (user_id, username, f"Имя {username}", seed_password_hash, role))
            token = hashlib.sha512(f"fixture-token-{username}".encode()).hexdigest()
            db.execute("INSERT INTO ApiTokens(id,token,datetime,expires_at,user_id) VALUES(?,?,?,?,?)",
                       (user_id, hashlib.sha256(token.encode()).hexdigest(), "2026-01-01T00:00:00",
                        "2099-01-01T00:00:00", user_id))
        db.executemany("INSERT INTO Funds(id,name,description,type,user_id) VALUES(?,?,?,?,1)", [
            (1, "Main fund", "Основной фонд", "for_stats"),
            (2, "Second fund", "Второй фонд", "for_stats"),
            (3, "HIDDEN NO STATS", "Технический фонд", "no_stats"),
            (4, "Unassigned fund", "Фонд другого администратора", "for_stats"),
        ])
        db.executemany("INSERT INTO Rights(user_id,fund_id) VALUES(?,?)", [
            (2, 1), (2, 2), (3, 1), (3, 4), (4, 1), (4, 2), (5, 1), (6, 1), (6, 3),
        ])
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def users(app):
    with app.app_context():
        return {row["username"]: dict(row) for row in get_db().execute("SELECT * FROM Users")}


@pytest.fixture
def api(client):
    def request(method, path, username="admin", data=None, **kwargs):
        token = hashlib.sha512(f"fixture-token-{username}".encode()).hexdigest()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        if data is not None:
            kwargs["json"] = data
        return client.open(path, method=method, headers=headers, **kwargs)
    return request


@pytest.fixture
def login(client):
    def perform(username="admin", password=PASSWORD):
        client.get("/login")
        with client.session_transaction() as session:
            csrf = session["_csrf"]
        return client.post("/login", data={"username": username, "password": password, "csrf_token": csrf})
    return perform


@pytest.fixture
def html_post(client):
    def perform(path, data=None, **kwargs):
        with client.session_transaction() as session:
            csrf = session["_csrf"]
        return client.post(path, data={**(data or {}), "csrf_token": csrf}, **kwargs)
    return perform


@pytest.fixture
def seed_transaction(app, users):
    """Создать независимые обычные записи журнала для тестов прав и отчётности."""
    def create(*, username="admin", fund_id=1, kind="income", money=10000,
               day="2026-04-15T12:00:00", pay_type="Kaspi", name="Fixture operation", description=""):
        with app.app_context():
            cursor = get_db().execute("""INSERT INTO Transactions
                (name,description,money,type,pay_type,datetime,from_fund_id,to_fund_id,user_id)
                VALUES(?,?,?,?,?,?,?,?,?)""",
                (name, description, money, kind, pay_type, day,
                 fund_id if kind == "expense" else None, fund_id if kind == "income" else None,
                 users[username]["id"]))
            return cursor.lastrowid
    return create


@pytest.fixture
def rows(app):
    def query(sql, params=()):
        with app.app_context():
            return [dict(row) for row in get_db().execute(sql, params)]
    return query


@pytest.fixture
def balance(app, users):
    def query(fund_id):
        from app import services
        with app.app_context():
            return services.fund_detail(users["root"], fund_id)["balance"]
    return query
