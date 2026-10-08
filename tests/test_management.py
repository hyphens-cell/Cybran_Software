"""Управление Super Admin, секретность токенов и ограничения базы данных."""
import hashlib
import re
import sqlite3
from datetime import datetime

import pytest
from werkzeug.datastructures import MultiDict
from werkzeug.security import check_password_hash

from app import services as svc
from app.db import get_db


@pytest.mark.parametrize("role", ["Super Admin", "Admin", "Cashier", "Investor"])
def test_create_users_all_roles_and_no_password_leak(api, rows, role):
    response = api("POST", "/api/create_user", "root", {"username": "new_user", "fullname": "Новый пользователь",
        "role": role, "password": "NewPassword-123"})
    assert response.status_code == 201
    assert response.json["role"] == role
    assert "password" not in str(response.json) and "hash" not in str(response.json)
    stored = rows("SELECT * FROM Users WHERE username='new_user'")[0]
    assert stored["password_hash"].startswith("pbkdf2:sha256:")
    assert check_password_hash(stored["password_hash"], "NewPassword-123")


def test_user_edit_search_filter_password_reset_and_invalidation(api, client, login, html_post, rows):
    assert login("cashier").status_code == 302
    response = api("PUT", "/api/users/4/edit_user", "root", {"fullname": "Мария Кассир", "role": "Admin"})
    assert response.status_code == 200
    assert rows("SELECT fullname,role FROM Users WHERE id=4") == [{"fullname": "Мария Кассир", "role": "Admin"}]
    assert client.get("/transactions").status_code == 302
    assert login("root").status_code == 302
    response = client.get("/users?search=Мария&role=Admin")
    assert response.status_code == 200 and "Мария Кассир" in response.get_data(as_text=True)
    assert html_post("/users/4/password", {"password": "ResetPassword-456"}).status_code == 302
    assert login("cashier").status_code == 401
    assert login("cashier", "ResetPassword-456").status_code == 302


def test_user_validation_and_case_insensitive_uniqueness(api):
    base = {"username": "new", "fullname": "Новый", "password": "SafePassword-123", "role": "Admin"}
    assert api("POST", "/api/create_user", "root", {**base, "role": "Owner"}).status_code == 400
    assert api("POST", "/api/create_user", "root", {**base, "username": "A" * 51}).status_code == 400
    assert api("POST", "/api/create_user", "root", {**base, "username": "ADMIN"}).status_code == 409
    assert api("PATCH", "/api/users/4/block", "root", {"is_active": "false"}).status_code == 400


def test_super_admin_cannot_block_or_downgrade_own_account(api, client, login, html_post, rows):
    assert login("root").status_code == 302

    listing = client.get("/users").get_data(as_text=True)
    assert "Это вы" in listing
    assert "Собственную учётную запись нельзя блокировать" in listing
    edit_page = client.get("/users/1/edit").get_data(as_text=True)
    assert "Роль вашей учётной записи защищена" in edit_page
    assert 'id="role"' in edit_page and "disabled" in edit_page

    assert api("PATCH", "/api/users/1/block", "root", {"is_active": False}).status_code == 409
    assert api("PUT", "/api/users/1/edit_user", "root", {"role": "Investor"}).status_code == 409
    assert html_post("/users/1/block", {"is_active": "0"}).status_code == 409
    response = html_post("/users/1/edit", {
        "username": "root", "fullname": "Имя root", "role": "Investor",
    })
    assert response.status_code == 409
    assert rows("SELECT role,is_active FROM Users WHERE id=1") == [
        {"role": "Super Admin", "is_active": 1}
    ]


@pytest.mark.parametrize("bad_value", [None, "false", "", "yes"])
def test_html_block_requires_explicit_boolean_flag(client, login, rows, bad_value):
    assert login("root").status_code == 302
    with client.session_transaction() as session:
        data = {"csrf_token": session["_csrf"]}
    if bad_value is not None:
        data["is_active"] = bad_value
    response = client.post("/users/4/block", data=data)
    assert response.status_code == 400
    assert rows("SELECT is_active FROM Users WHERE id=4") == [{"is_active": 1}]


@pytest.mark.parametrize("bad_password", ["", None, False, 123])
def test_edit_user_rejects_explicit_invalid_password(api, rows, bad_password):
    before = rows("SELECT password_hash,auth_version FROM Users WHERE id=4")[0]
    response = api("PUT", "/api/users/4/edit_user", "root", {"password": bad_password})
    assert response.status_code == 400
    assert rows("SELECT password_hash,auth_version FROM Users WHERE id=4")[0] == before


def test_active_super_admin_invariant_survives_stale_concurrent_actor(app, users):
    with app.app_context():
        db = get_db()
        db.execute("""INSERT INTO Users(id,username,fullname,password_hash,role)
                    SELECT 7,'backup-root','Резервный администратор',password_hash,'Super Admin'
                    FROM Users WHERE id=1""")
        stale_backup = dict(db.execute("SELECT * FROM Users WHERE id=7").fetchone())

        svc.block_user(users["root"], 7, False)
        with pytest.raises(svc.DomainError) as error:
            svc.block_user(stale_backup, 1, False)

        assert error.value.status == 409
        assert db.execute("""SELECT COUNT(*) FROM Users
                              WHERE role='Super Admin' AND is_active=1""").fetchone()[0] == 1


def test_create_edit_archive_fund_and_metadata(api, client, login, html_post, rows):
    response = api("POST", "/api/create_fund", "root", {"name": "Новый фонд", "description": "Проект", "type": "no_stats"})
    assert response.status_code == 201
    fund_id = response.json["id"]
    assert response.json["user_id"] == 1
    assert login("root").status_code == 302
    assert html_post(f"/funds/{fund_id}/edit", {"name": "Исправленный", "description": "Развитие", "type": "for_stats"}).status_code == 302
    stored = rows("SELECT name,description,type FROM Funds WHERE id=?", (fund_id,))[0]
    assert stored == {"name": "Исправленный", "description": "Развитие", "type": "for_stats"}
    assert api("PATCH", f"/api/funds/{fund_id}/archive", "root").status_code == 200
    assert rows("SELECT is_active FROM Funds WHERE id=?", (fund_id,)) == [{"is_active": 0}]
    assert api("PATCH", f"/api/funds/{fund_id}/archive", "root").status_code == 409
    restored = api("PATCH", f"/api/funds/{fund_id}/restore", "root")
    assert restored.status_code == 200
    assert restored.json["is_active"] == 1
    assert rows("SELECT is_active FROM Funds WHERE id=?", (fund_id,)) == [{"is_active": 1}]
    assert api("POST", "/api/transactions/add", "root", {"fund_id": fund_id, "money": 100, "type": "income", "pay_type": "Kaspi"}).status_code == 201
    assert api("POST", "/api/create_fund", "root", {"name": "Bad", "type": "custom"}).status_code == 400


def test_html_archive_requires_exact_fund_name_and_restore_is_available(client, login, html_post, rows):
    assert login("root").status_code == 302
    assert html_post("/funds/1/archive", {"confirm_fund_name": "не тот фонд"}).status_code == 302
    assert rows("SELECT is_active FROM Funds WHERE id=1") == [{"is_active": 1}]
    assert html_post("/funds/1/archive", {"confirm_fund_name": "Main fund"}).status_code == 302
    assert rows("SELECT is_active FROM Funds WHERE id=1") == [{"is_active": 0}]
    page = client.get("/funds/1/edit")
    assert page.status_code == 200 and "Восстановить фонд" in page.get_data(as_text=True)
    assert html_post("/funds/1/restore").status_code == 302
    assert rows("SELECT is_active FROM Funds WHERE id=1") == [{"is_active": 1}]


def test_grant_revoke_right_changes_existing_token_immediately(api):
    assert {row["id"] for row in api("GET", "/api/funds").json} == {1, 2}
    response = api("POST", "/api/rights", "root", {"user_id": 2, "fund_id": 4})
    assert response.status_code == 201
    assert {row["id"] for row in api("GET", "/api/funds").json} == {1, 2, 4}
    assert api("DELETE", "/api/rights/2/4", "root").status_code == 204
    assert {row["id"] for row in api("GET", "/api/funds").json} == {1, 2}
    assert api("POST", "/api/rights", "root", {"user_id": 999, "fund_id": 4}).status_code == 404


def test_mass_rights_form_and_invalid_replacement_are_atomic(app, users, client, login, rows):
    assert login("root").status_code == 302
    with client.session_transaction() as session:
        csrf = session["_csrf"]
    response = client.post("/rights", data=MultiDict([
        ("user_id", "4"), ("fund_ids", "1"), ("fund_ids", "2"), ("fund_ids", "4"), ("csrf_token", csrf)]))
    assert response.status_code == 302
    assert {row["fund_id"] for row in rows("SELECT fund_id FROM Rights WHERE user_id=4")} == {1, 2, 4}
    with app.app_context():
        with pytest.raises(svc.DomainError):
            svc.set_rights(users["root"], 4, [1, 999])
    assert {row["fund_id"] for row in rows("SELECT fund_id FROM Rights WHERE user_id=4")} == {1, 2, 4}


def test_token_generated_once_hash_only_and_revocation(app, client, login, html_post, api, rows):
    assert login("root").status_code == 302
    response = html_post("/tokens", {"user_id": 2})
    assert response.status_code == 200
    match = re.search(r'id="generated-token"[^>]*>([0-9a-f]{128})</textarea>', response.get_data(as_text=True))
    assert match, "Однократное раскрытие токена должно содержать ровно 128 символов."
    token = match.group(1)
    stored = rows("SELECT * FROM ApiTokens ORDER BY id DESC LIMIT 1")[0]
    assert stored["token"] == hashlib.sha256(token.encode()).hexdigest()
    assert stored["token"] != token and stored["user_id"] == 2
    assert datetime.fromisoformat(stored["expires_at"]) - datetime.fromisoformat(stored["datetime"]) == app.config["API_TOKEN_LIFETIME"]
    listing = client.get("/tokens").get_data(as_text=True)
    assert token not in listing and stored["token"] not in listing
    assert response.headers["Cache-Control"] == "no-store"
    assert client.get("/api/funds", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    assert api("DELETE", f"/api/tokens/{stored['id']}", "root").status_code == 204
    assert client.get("/api/funds", headers={"Authorization": f"Bearer {token}"}).status_code == 401
    assert rows("SELECT active FROM ApiTokens WHERE id=?", (stored["id"],)) == [{"active": 0}]


def test_password_reset_revokes_existing_api_tokens(api, client, login, html_post, rows):
    assert api("GET", "/api/funds", "admin").status_code == 200
    assert login("root").status_code == 302
    assert html_post("/users/2/password", {"password": "ReplacementPassword-789"}).status_code == 302
    assert api("GET", "/api/funds", "admin").status_code == 401
    assert rows("SELECT active FROM ApiTokens WHERE user_id=2") == [{"active": 0}]


def test_expired_api_token_is_rejected(api, app):
    with app.app_context():
        get_db().execute("UPDATE ApiTokens SET expires_at='2000-01-01T00:00:00' WHERE user_id=2")
    assert api("GET", "/api/funds", "admin").status_code == 401


def test_token_uniqueness_and_blocked_owner(app, users):
    with app.app_context():
        first = svc.create_token(users["root"], users["admin"]["id"])
        second = svc.create_token(users["root"], users["admin"]["id"])
        assert len(first["token"]) == len(second["token"]) == 128
        assert first["token"] != second["token"]
        svc.block_user(users["root"], users["admin"]["id"], False)
        with pytest.raises(svc.DomainError) as error:
            svc.create_token(users["root"], users["admin"]["id"])
        assert error.value.status == 409
        assert all("token" not in row for row in svc.list_tokens(users["root"]))


def test_database_constraints_enforce_relationships_and_types(app):
    with app.app_context():
        db = get_db()
        assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO Rights(user_id,fund_id) VALUES(999,1)")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO Rights(user_id,fund_id) VALUES(2,1)")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO Funds(name,type,user_id) VALUES('invalid','unknown',1)")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("""INSERT INTO Transactions(name,money,type,pay_type,datetime,to_fund_id,user_id)
                VALUES('invalid',1.25,'income','Kaspi','2026-01-01',1,1)""")


def test_untrusted_html_is_escaped_and_sql_text_is_data(client, login, api):
    response = api("POST", "/api/transactions/add", data={"fund_id": 1, "money": 100,
        "type": "income", "pay_type": "Kaspi", "name": "<script>alert(1)</script>",
        "description": "'; DROP TABLE Funds; --"})
    assert response.status_code == 201
    assert login("admin").status_code == 302
    response = client.get("/transactions")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "<script>alert(1)</script>" not in text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in text
    assert len(api("GET", "/api/funds").json) == 2


def test_required_schema_columns_exist(app):
    required = {
        "Users": {"id", "username", "fullname", "password_hash", "role", "is_active"},
        "Rights": {"id", "fund_id", "user_id"},
        "ApiTokens": {"id", "token", "active", "datetime", "expires_at", "user_id"},
        "WebSessions": {"id", "session_hash", "user_id", "auth_version", "created_at", "last_seen_at",
                        "expires_at", "ip_address", "user_agent", "revoked_at", "revoked_by"},
        "LoginAttempts": {"key_hash", "attempts", "window_started_at"},
        "Funds": {"id", "name", "description", "type", "user_id", "is_active"},
        "Transactions": {"id", "name", "description", "money", "type", "pay_type", "datetime",
                         "from_fund_id", "to_fund_id", "user_id"},
    }
    with app.app_context():
        for table, columns in required.items():
            actual = {row["name"] for row in get_db().execute(f"PRAGMA table_info({table})")}
            assert columns <= actual
