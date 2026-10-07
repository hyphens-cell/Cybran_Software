"""HTML permissions are enforced for direct requests with valid CSRF tokens."""
import pytest

from app import services as svc
from app.db import get_db


@pytest.mark.parametrize("username,destination", [("root", "/dashboard"), ("admin", "/funds"),
                                                  ("cashier", "/cashier"), ("investor", "/dashboard")])
def test_login_role_landing_and_logout(client, login, html_post, username, destination):
    assert login(username).status_code == 302
    response = client.get("/")
    assert response.status_code == 302 and response.location.endswith(destination)
    assert client.get(destination).status_code == 200
    assert html_post("/logout").status_code == 302
    assert client.get(destination).status_code == 302


def test_bad_password_and_csrf(client, login):
    assert login("admin", "wrong-password").status_code == 401
    assert client.get("/funds").status_code == 302
    assert client.post("/login", data={"username": "admin", "password": "CorrectPassword-123"}).status_code == 400
    assert login("admin").status_code == 302
    assert client.post("/transactions/new", data={"amount": "10", "fund_id": 1,
        "type": "income", "pay_type": "Kaspi"}).status_code == 400


def test_blocked_user_invalidates_login_session_and_api(api, client, login, rows):
    assert login("admin").status_code == 302
    assert api("PATCH", "/api/users/2/block", "root", {"is_active": False}).status_code == 200
    assert rows("SELECT is_active FROM Users WHERE id=2") == [{"is_active": 0}]
    assert client.get("/funds").status_code == 302
    assert api("GET", "/api/funds").status_code == 401
    assert login("admin").status_code == 401
    assert api("PATCH", "/api/users/2/block", "root", {"is_active": True}).status_code == 200
    assert login("admin").status_code == 302
    assert api("GET", "/api/funds").status_code == 200


@pytest.mark.parametrize("username", ["admin", "cashier", "investor"])
@pytest.mark.parametrize("path", ["/users", "/users/new", "/funds/new", "/funds/1/edit", "/rights", "/tokens"])
def test_non_super_admin_cannot_open_management(client, login, username, path):
    assert login(username).status_code == 302
    assert client.get(path).status_code == 403


@pytest.mark.parametrize("username", ["admin", "cashier"])
def test_global_dashboard_and_exports_role_enforcement(client, login, username):
    assert login(username).status_code == 302
    assert client.get("/dashboard").status_code == 403
    assert client.get("/reports/export?format=csv").status_code == 403


@pytest.mark.parametrize("path", ["/transactions/new", "/transfers/new", "/funds/new",
    "/funds/1/archive", "/transactions/1/edit", "/transactions/1/delete", "/transactions/1/cancel",
    "/users/4/block", "/rights", "/tokens"])
def test_investor_read_only_even_for_forged_post(client, login, html_post, path):
    assert login("investor").status_code == 302
    assert html_post(path, {"amount": "10.00", "fund_id": 1, "type": "income", "pay_type": "Kaspi"}).status_code == 403


def test_investor_details_require_rights_and_exclude_no_stats(client, login, seed_transaction):
    seed_transaction(fund_id=1)
    seed_transaction(fund_id=3, username="root", name="NEVER DISCLOSE")
    assert login("investor").status_code == 302
    assert client.get("/funds/1").status_code == 200
    assert client.get("/funds/2").status_code == 403
    assert client.get("/funds/3").status_code == 403
    assert client.get("/transactions?fund_id=3").status_code == 403
    assert "NEVER DISCLOSE" not in client.get("/transactions").get_data(as_text=True)
    assert "HIDDEN NO STATS" not in client.get("/dashboard").get_data(as_text=True)


@pytest.mark.parametrize("username", ["admin", "cashier"])
def test_html_foreign_fund_idor(client, login, html_post, seed_transaction, balance, username):
    foreign_id = seed_transaction(username="other_admin", fund_id=4)
    own_id = seed_transaction(username=username, fund_id=1)
    assert login(username).status_code == 302
    assert client.get("/funds/4").status_code == 403
    assert client.get("/transactions?fund_id=4").status_code == 403
    assert html_post("/transactions/new", {"fund_id": 4, "amount": "15.25", "type": "income", "pay_type": "Kaspi"}).status_code == 403
    assert html_post(f"/transactions/{foreign_id}/delete").status_code == 403
    assert html_post(f"/transactions/{own_id}/edit", {"fund_id": 4, "amount": "15.25", "type": "income", "pay_type": "Kaspi"}).status_code == 403
    assert (balance(1), balance(4)) == (10000, 10000)


def test_cashier_income_expense_history_and_no_transfer(client, login, html_post, rows, balance):
    assert login("cashier").status_code == 302
    assert "Принять оплату" in client.get("/cashier").get_data(as_text=True)
    assert html_post("/cashier", {"fund_id": 1, "amount": "10,01", "pay_type": "Kaspi", "description": "Оплата"}).status_code == 302
    assert html_post("/transactions/new", {"fund_id": 1, "amount": "2.02", "pay_type": "Наличные", "type": "expense"}).status_code == 302
    assert balance(1) == 799
    assert {row["type"] for row in rows("SELECT type FROM Transactions")} == {"income", "expense"}
    assert client.get("/shifts").status_code == 200
    assert html_post("/transfers/new", {"from_fund_id": 1, "to_fund_id": 2, "amount": "1.00"}).status_code == 403
    assert client.get("/transfers/new").status_code == 403


def test_cashier_cancels_only_last_own_transaction(client, login, html_post, seed_transaction, rows, balance):
    old = seed_transaction(username="cashier", day="2026-05-05T00:00:00")
    other = seed_transaction(username="other_cashier")
    last = seed_transaction(username="cashier", day="2026-01-01T00:00:00", money=200)
    assert login("cashier").status_code == 302
    assert html_post(f"/transactions/{old}/cancel").status_code == 403
    assert html_post(f"/transactions/{other}/cancel").status_code == 403
    assert html_post(f"/transactions/{last}/edit", {"amount": "1.00"}).status_code == 403
    assert html_post(f"/transactions/{last}/delete").status_code == 403
    assert html_post(f"/transactions/{last}/cancel").status_code == 302
    assert {row["id"] for row in rows("SELECT id FROM Transactions")} == {old, other}
    assert balance(1) == 20000


def test_cashier_cannot_cancel_last_after_right_is_revoked(api, client, login, html_post, seed_transaction, rows):
    last = seed_transaction(username="cashier", fund_id=2)
    assert login("cashier").status_code == 302
    assert api("DELETE", "/api/rights/4/2", "root").status_code == 204
    assert html_post(f"/transactions/{last}/cancel").status_code == 403
    assert len(rows("SELECT id FROM Transactions")) == 1


def test_last_own_is_not_last_in_current_fund_filter(client, login, html_post, seed_transaction):
    first_fund = seed_transaction(username="cashier", fund_id=1)
    seed_transaction(username="cashier", fund_id=2)
    assert login("cashier").status_code == 302
    assert client.get("/transactions?fund_id=1").status_code == 200
    assert html_post(f"/transactions/{first_fund}/cancel").status_code == 403


@pytest.mark.parametrize("amount", ["NaN", "Infinity", "-1", "0", "1.001", "92233720368547758.08"])
def test_html_money_rejects_non_finite_fractional_or_overflow(login, html_post, rows, amount):
    assert login("cashier").status_code == 302
    response = html_post("/cashier", {"fund_id": 1, "amount": amount, "pay_type": "Kaspi"})
    assert response.status_code == 400
    assert rows("SELECT id FROM Transactions") == []


def test_session_and_api_permissions_refresh_after_role_change(api, client, login):
    assert login("admin").status_code == 302
    assert api("PUT", "/api/users/2/edit_user", "root", {"role": "Investor"}).status_code == 200
    assert client.get("/funds").status_code == 302
    assert api("GET", "/api/funds").status_code == 403


@pytest.mark.parametrize("optional", [{}, {"pay_type": ""}])
def test_html_transfer_accepts_optional_empty_payment_type(login, html_post, rows, balance, optional):
    assert login("admin").status_code == 302
    response = html_post("/transfers/new", {"from_fund_id": 1, "to_fund_id": 2,
        "amount": "4.25", "description": "Перемещение", **optional})
    assert response.status_code == 302
    assert (balance(1), balance(2)) == (-425, 425)
    assert len(rows("SELECT id FROM Transactions")) == 2


def test_cashier_shift_is_day_worked_and_contains_other_authors(client, login, seed_transaction):
    seed_transaction(username="cashier", name="Own shift payment", day="2026-04-15T12:00:00")
    seed_transaction(username="other_cashier", name="Same day other author", day="2026-04-15T13:00:00")
    seed_transaction(username="other_cashier", name="Day without own work", day="2026-04-16T12:00:00")
    assert login("cashier").status_code == 302
    response = client.get("/shifts")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Own shift payment" in text and "Same day other author" in text
    assert "Day without own work" not in text
