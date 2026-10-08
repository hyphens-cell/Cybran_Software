"""Точные методы, пути API и контракты ролей со страниц 8–9 ТЗ."""
import pytest


SUPER_ENDPOINTS = [
    ("POST", "/api/create_user"), ("PUT", "/api/users/4/edit_user"),
    ("PATCH", "/api/users/4/block"), ("POST", "/api/create_fund"),
    ("PATCH", "/api/funds/1/archive"), ("PATCH", "/api/funds/1/restore"),
    ("POST", "/api/rights"),
    ("DELETE", "/api/rights/4/1"), ("DELETE", "/api/tokens/4"),
    ("PUT", "/api/transactions/1"), ("DELETE", "/api/transactions/1"),
]
ADMIN_ENDPOINTS = [
    ("GET", "/api/funds"), ("POST", "/api/transactions/add"),
    ("POST", "/api/transactions/add_transfer"), ("GET", "/api/transactions"),
    ("PUT", "/api/transactions/1/edit"), ("DELETE", "/api/transactions/1/delete"),
]


@pytest.mark.parametrize("username", ["admin", "cashier", "investor"])
@pytest.mark.parametrize("method,path", SUPER_ENDPOINTS)
def test_super_admin_api_role_matrix(api, username, method, path):
    response = api(method, path, username, data={})
    assert response.status_code == 403


@pytest.mark.parametrize("username", ["cashier", "investor"])
@pytest.mark.parametrize("method,path", ADMIN_ENDPOINTS)
def test_admin_api_does_not_inherit_cashier_or_investor_ui_rights(api, username, method, path):
    assert api(method, path, username, data={}).status_code == 403


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer invalid"},
    {"Authorization": "Bearer " + "x" * 128}, {"Authorization": "Basic " + "x" * 128}])
def test_api_rejects_missing_or_invalid_token(client, headers):
    response = client.get("/api/funds", headers=headers)
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_cookie_session_does_not_authenticate_api(client, login):
    assert login("root").status_code == 302
    assert client.get("/api/funds").status_code == 401


def test_fund_and_transaction_lists_are_scoped(api, seed_transaction):
    own = seed_transaction(fund_id=1)
    shared = seed_transaction(username="other_admin", fund_id=2)
    seed_transaction(username="other_admin", fund_id=4)
    seed_transaction(username="root", fund_id=3)
    assert {row["id"] for row in api("GET", "/api/funds").json} == {1, 2}
    assert {row["id"] for row in api("GET", "/api/transactions").json} == {own, shared}
    assert len(api("GET", "/api/funds", "root").json) == 4
    assert api("GET", "/api/transactions?fund_id=4").status_code == 403
    assert api("GET", "/api/transactions?fund_id=3").status_code == 403


def test_income_expense_and_integer_balances(api, balance, rows):
    income = api("POST", "/api/transactions/add", data={"fund_id": 1, "money": 10001,
        "type": "income", "pay_type": "Kaspi", "description": "Оплата"})
    assert income.status_code == 201
    assert income.json["money"] == 10001 and type(income.json["money"]) is int
    expense = api("POST", "/api/transactions/add", data={"fund_id": 1, "money": 2501,
        "type": "expense", "pay_type": "Наличные"})
    assert expense.status_code == 201
    assert balance(1) == 7500
    assert rows("SELECT DISTINCT typeof(money) AS kind FROM Transactions") == [{"kind": "integer"}]


@pytest.mark.parametrize("money", [0, -1, 1.5, "100", True, False, None, 9223372036854775808])
def test_invalid_money_cannot_create_or_edit(api, rows, seed_transaction, money):
    transaction_id = seed_transaction()
    response = api("POST", "/api/transactions/add", data={"fund_id": 1, "money": money,
        "type": "income", "pay_type": "Kaspi"})
    assert response.status_code == 400
    assert api("PUT", f"/api/transactions/{transaction_id}/edit", data={"money": money}).status_code == 400
    assert rows("SELECT money FROM Transactions") == [{"money": 10000}]


@pytest.mark.parametrize("data", [
    {"fund_id": 1, "money": 10, "type": "income"},
    {"fund_id": 1, "money": 10, "type": "income", "pay_type": ""},
    {"fund_id": 1, "money": 10, "type": "inter-transaction", "pay_type": "Kaspi"},
    {"fund_id": 1, "money": 10, "type": "invalid", "pay_type": "Kaspi"},
])
def test_required_pay_type_and_transaction_enum(api, rows, data):
    assert api("POST", "/api/transactions/add", data=data).status_code == 400
    assert rows("SELECT id FROM Transactions") == []


def test_free_text_pay_type_and_negative_balance_are_supported(api, balance):
    response = api("POST", "/api/transactions/add", data={"fund_id": 1, "money": 125,
        "type": "expense", "pay_type": "Банковский перевод"})
    assert response.status_code == 201
    assert balance(1) == -125


def test_foreign_fund_create_and_edit_are_forbidden(api, seed_transaction, balance):
    transaction_id = seed_transaction()
    payload = {"fund_id": 4, "money": 10, "type": "income", "pay_type": "Kaspi"}
    assert api("POST", "/api/transactions/add", data=payload).status_code == 403
    assert api("PUT", f"/api/transactions/{transaction_id}/edit", data={"fund_id": 4}).status_code == 403
    assert balance(1) == 10000 and balance(4) == 0


@pytest.mark.parametrize("username,allowed", [("admin", True), ("cashier", True),
                                               ("other_admin", False), ("root", False)])
def test_admin_edit_delete_author_rule(api, seed_transaction, balance, username, allowed):
    transaction_id = seed_transaction(username=username)
    response = api("PUT", f"/api/transactions/{transaction_id}/edit", data={"money": 777})
    assert response.status_code == (200 if allowed else 404)
    assert balance(1) == (777 if allowed else 10000)
    response = api("DELETE", f"/api/transactions/{transaction_id}/delete")
    assert response.status_code == (204 if allowed else 404)
    assert balance(1) == (0 if allowed else 10000)


def test_global_edit_delete_all_authors(api, seed_transaction, balance):
    transaction_id = seed_transaction(username="other_admin", fund_id=4)
    assert api("PUT", f"/api/transactions/{transaction_id}", "root", {"money": 333}).status_code == 200
    assert balance(4) == 333
    assert api("DELETE", f"/api/transactions/{transaction_id}", "root").status_code == 204
    assert balance(4) == 0


def test_filters_include_whole_dates_and_combine(api, seed_transaction):
    chosen = seed_transaction(day="2026-04-30T23:59:59", pay_type="Kaspi")
    seed_transaction(day="2026-05-01T00:00:00", pay_type="Kaspi")
    seed_transaction(day="2026-04-30T12:00:00", pay_type="Карта")
    seed_transaction(day="2026-04-30T12:00:00", pay_type="Kaspi", kind="expense")
    response = api("GET", "/api/transactions", query_string={"date_from": "2026-04-30",
        "date_to": "2026-04-30", "type": "income", "pay_type": "Kaspi", "fund_id": 1})
    assert response.status_code == 200
    assert [row["id"] for row in response.json] == [chosen]


@pytest.mark.parametrize("query", ["date_from=bad", "date_from=2026-05-02&date_to=2026-05-01",
                                   "type=unknown", "fund_id=-1"])
def test_invalid_filters_fail_safely(api, query):
    assert api("GET", f"/api/transactions?{query}").status_code == 400


def test_api_rejects_non_object_json_and_wrong_content_type(api):
    assert api("POST", "/api/transactions/add", data=[]).status_code == 400
    assert api("POST", "/api/transactions/add", data="text").status_code == 400
    assert api("POST", "/api/transactions/add").status_code == 415


def test_author_cannot_be_spoofed_by_client(api, rows):
    response = api("POST", "/api/transactions/add", data={"fund_id": 1, "money": 1,
        "type": "income", "pay_type": "Kaspi", "user_id": 1})
    assert response.status_code == 201 and response.json["user_id"] == 2
    transaction_id = response.json["id"]
    assert api("PUT", f"/api/transactions/{transaction_id}/edit", data={"user_id": 1}).status_code == 200
    assert rows("SELECT user_id FROM Transactions WHERE id=?", (transaction_id,)) == [{"user_id": 2}]
