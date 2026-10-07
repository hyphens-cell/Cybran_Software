"""Server-side browser session lifecycle and Super Admin controls."""
from datetime import datetime

from app.db import get_db


PASSWORD = "CorrectPassword-123"


def sign_in(client, username):
    client.get("/login")
    with client.session_transaction() as browser_session:
        csrf = browser_session["_csrf"]
    return client.post("/login", data={"username": username, "password": PASSWORD, "csrf_token": csrf})


def post_with_csrf(client, path, data=None):
    with client.session_transaction() as browser_session:
        csrf = browser_session["_csrf"]
    return client.post(path, data={**(data or {}), "csrf_token": csrf})


def test_login_creates_visible_server_session_with_absolute_24_hour_lifetime(app, client):
    assert sign_in(client, "root").status_code == 302
    with app.app_context():
        row = dict(get_db().execute("SELECT * FROM WebSessions").fetchone())
    assert row["session_hash"] and len(row["session_hash"]) == 64
    assert row["revoked_at"] is None
    assert datetime.fromisoformat(row["expires_at"]) - datetime.fromisoformat(row["created_at"]) == app.config["WEB_SESSION_LIFETIME"]

    response = client.get("/sessions")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Активные сессии" in text and "Максимальный срок — 24 часа" in text
    assert "Текущая" in text and "root" in text


def test_only_super_admin_can_view_or_revoke_sessions(app):
    client = app.test_client()
    assert sign_in(client, "admin").status_code == 302
    assert client.get("/sessions").status_code == 403
    assert post_with_csrf(client, "/sessions/1/revoke").status_code == 403
    assert post_with_csrf(client, "/sessions/revoke-all", {"scope": "all"}).status_code == 403


def test_super_admin_can_revoke_another_live_session(app):
    root_client = app.test_client()
    user_client = app.test_client()
    assert sign_in(root_client, "root").status_code == 302
    assert sign_in(user_client, "admin").status_code == 302
    with app.app_context():
        session_id = get_db().execute("SELECT id FROM WebSessions WHERE user_id=2").fetchone()["id"]

    assert post_with_csrf(root_client, f"/sessions/{session_id}/revoke").status_code == 302
    response = user_client.get("/funds")
    assert response.status_code == 302 and "/login?ended=1" in response.location


def test_logout_revokes_a_copied_cookie(app):
    user_client = app.test_client()
    assert sign_in(user_client, "admin").status_code == 302
    cookie_name = app.config["SESSION_COOKIE_NAME"]
    copied_cookie = user_client.get_cookie(cookie_name).value
    assert post_with_csrf(user_client, "/logout").status_code == 302

    replay_client = app.test_client()
    replay_client.set_cookie(cookie_name, copied_cookie)
    response = replay_client.get("/funds")
    assert response.status_code == 302 and "/login?ended=1" in response.location


def test_expired_session_is_rejected_even_when_cookie_is_present(app):
    client = app.test_client()
    assert sign_in(client, "admin").status_code == 302
    with app.app_context():
        get_db().execute("UPDATE WebSessions SET expires_at='2000-01-01T00:00:00'")
    response = client.get("/funds")
    assert response.status_code == 302 and "/login?ended=expired" in response.location


def test_old_session_rows_are_pruned_without_removing_recent_audit_rows(app, client):
    assert sign_in(client, "admin").status_code == 302
    with app.app_context():
        db = get_db()
        db.execute("UPDATE WebSessions SET expires_at='2000-01-01T00:00:00', revoked_at='2000-01-01T00:00:00'")
    client.get("/login")
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM WebSessions").fetchone()[0] == 0


def test_revoke_all_others_preserves_current_super_admin_session(app):
    root_client = app.test_client()
    user_client = app.test_client()
    assert sign_in(root_client, "root").status_code == 302
    assert sign_in(user_client, "cashier").status_code == 302

    response = post_with_csrf(root_client, "/sessions/revoke-all", {"scope": "others"})
    assert response.status_code == 302 and response.location.endswith("/sessions")
    assert root_client.get("/sessions").status_code == 200
    assert user_client.get("/cashier").status_code == 302
    with app.app_context():
        active = get_db().execute("SELECT COUNT(*) FROM WebSessions WHERE revoked_at IS NULL").fetchone()[0]
    assert active == 1


def test_revoke_all_including_current_logs_super_admin_out(app):
    client = app.test_client()
    assert sign_in(client, "root").status_code == 302
    response = post_with_csrf(client, "/sessions/revoke-all", {"scope": "all"})
    assert response.status_code == 302 and "/login?ended=all" in response.location
    assert client.get("/sessions").status_code == 302
