"""Real SQLite failures, paired transfers, balances, and access on both sides."""
import pytest

from app import services as svc
from app.db import get_db


def transfer_payload(**changes):
    return {"from_fund_id": 1, "to_fund_id": 2, "money": 2300,
            "description": "Внутреннее движение", **changes}


def test_transfer_has_two_rows_and_one_logical_history_entry(api, rows, balance, seed_transaction):
    seed_transaction(money=10000)
    response = api("POST", "/api/transactions/add_transfer", data=transfer_payload())
    assert response.status_code == 201
    pair = rows("SELECT * FROM Transactions WHERE type='inter-transaction'")
    assert len(pair) == 2
    assert {row["transfer_side"] for row in pair} == {"debit", "credit"}
    assert len({row["transfer_id"] for row in pair}) == 1
    assert all(row["from_fund_id"] == 1 and row["to_fund_id"] == 2 and row["money"] == 2300 for row in pair)
    assert (balance(1), balance(2)) == (7700, 2300)
    history = api("GET", "/api/transactions?type=inter-transaction").json
    assert len(history) == 1
    assert len(api("GET", "/api/transactions?fund_id=1").json) == 2
    assert len(api("GET", "/api/transactions?fund_id=2").json) == 1
    funds = {row["id"]: row for row in api("GET", "/api/funds").json}
    assert funds[1]["transaction_count"] == 2 and funds[2]["transaction_count"] == 1


@pytest.mark.parametrize("source,target", [(1, 4), (4, 1), (3, 4)])
def test_transfer_requires_both_rights(api, rows, source, target):
    assert api("POST", "/api/transactions/add_transfer", data=transfer_payload(
        from_fund_id=source, to_fund_id=target)).status_code == 403
    assert rows("SELECT id FROM Transactions") == []


def test_self_transfer_and_invalid_amount_rejected(api, rows):
    assert api("POST", "/api/transactions/add_transfer", data=transfer_payload(to_fund_id=1)).status_code == 400
    assert api("POST", "/api/transactions/add_transfer", data=transfer_payload(money=1.01)).status_code == 400
    assert rows("SELECT id FROM Transactions") == []


def test_transfer_creation_rolls_back_when_credit_insert_fails(app, users, rows, balance):
    with app.app_context():
        get_db().executescript("""CREATE TRIGGER reject_credit BEFORE INSERT ON Transactions
            WHEN NEW.transfer_side='credit' BEGIN SELECT RAISE(ABORT,'injected credit failure'); END;""")
        with pytest.raises(svc.DomainError) as error:
            svc.create_transfer(users["admin"], transfer_payload())
        assert error.value.status == 409
    assert rows("SELECT id FROM Transactions") == []
    assert balance(1) == balance(2) == 0


@pytest.mark.parametrize("action", ["edit", "delete"])
def test_pair_mutation_rolls_back_if_one_side_fails(app, users, api, rows, balance, action):
    created = api("POST", "/api/transactions/add_transfer", data=transfer_payload()).json
    original = rows("SELECT * FROM Transactions ORDER BY id")
    with app.app_context():
        event, row = ("UPDATE", "NEW") if action == "edit" else ("DELETE", "OLD")
        get_db().executescript(f"""CREATE TRIGGER reject_pair BEFORE {event} ON Transactions
            WHEN {row}.transfer_side='credit' BEGIN SELECT RAISE(ABORT,'injected paired mutation failure'); END;""")
        with pytest.raises(svc.DomainError) as error:
            if action == "edit":
                svc.edit_transaction(users["admin"], created["id"], {"money": 100})
            else:
                svc.delete_transaction(users["admin"], created["id"])
        assert error.value.status == 409
    assert rows("SELECT * FROM Transactions ORDER BY id") == original
    assert (balance(1), balance(2)) == (-2300, 2300)


def test_edit_and_delete_through_credit_id_keep_pair_consistent(api, rows, balance):
    result = api("POST", "/api/transactions/add_transfer", data=transfer_payload()).json
    credit_id = result["linked_transaction_id"]
    response = api("PUT", f"/api/transactions/{credit_id}/edit", data={"money": 751})
    assert response.status_code == 200
    assert [row["money"] for row in rows("SELECT money FROM Transactions")] == [751, 751]
    assert (balance(1), balance(2)) == (-751, 751)
    assert api("DELETE", f"/api/transactions/{credit_id}/delete").status_code == 204
    assert rows("SELECT id FROM Transactions") == []
    assert balance(1) == balance(2) == 0


def test_super_admin_can_move_transfer_endpoints_atomically(api, balance, rows):
    result = api("POST", "/api/transactions/add_transfer", data=transfer_payload()).json
    response = api("PUT", f"/api/transactions/{result['id']}", "root",
                   {"from_fund_id": 2, "to_fund_id": 4, "money": 800})
    assert response.status_code == 200
    assert (balance(1), balance(2), balance(4)) == (0, -800, 800)
    assert all(row["from_fund_id"] == 2 and row["to_fund_id"] == 4
               for row in rows("SELECT * FROM Transactions"))


def test_transfer_edit_checks_old_and_new_funds(api, rows):
    result = api("POST", "/api/transactions/add_transfer", data=transfer_payload()).json
    original = rows("SELECT * FROM Transactions ORDER BY id")
    assert api("PUT", f"/api/transactions/{result['id']}/edit", data={"to_fund_id": 4}).status_code == 403
    assert rows("SELECT * FROM Transactions ORDER BY id") == original
    assert api("DELETE", "/api/rights/2/2", "root").status_code == 204
    assert api("PUT", f"/api/transactions/{result['id']}/edit", data={"to_fund_id": 1}).status_code == 403
    assert api("DELETE", f"/api/transactions/{result['linked_transaction_id']}/delete").status_code == 403
    assert rows("SELECT * FROM Transactions ORDER BY id") == original


def test_transfer_cannot_turn_into_ordinary_income(api, rows):
    result = api("POST", "/api/transactions/add_transfer", data=transfer_payload()).json
    assert api("PUT", f"/api/transactions/{result['id']}/edit", data={"type": "income"}).status_code == 400
    assert len(rows("SELECT id FROM Transactions WHERE type='inter-transaction'")) == 2


def test_archiving_preserves_history_balances_and_global_stats(api, app, users, seed_transaction, balance, rows):
    seed_transaction(money=4567)
    assert api("PATCH", "/api/funds/1/archive", "root").status_code == 200
    assert rows("SELECT is_active FROM Funds WHERE id=1") == [{"is_active": 0}]
    assert balance(1) == 4567
    assert len(api("GET", "/api/transactions?fund_id=1").json) == 1
    assert api("POST", "/api/transactions/add", data={"fund_id": 1, "money": 100,
        "type": "income", "pay_type": "Kaspi"}).status_code == 409
    assert api("POST", "/api/transactions/add_transfer", data=transfer_payload()).status_code == 409
    with app.app_context():
        assert svc.dashboard(users["investor"])["balance"] == 4567


def test_inaccessible_counterpart_is_redacted_for_admin(api):
    response = api("POST", "/api/transactions/add_transfer", "root", transfer_payload(to_fund_id=4))
    assert response.status_code == 201
    result = api("GET", "/api/transactions").json
    assert len(result) == 1
    assert result[0]["from_fund_id"] == 1
    assert result[0]["to_fund_id"] is None
    assert "Unassigned fund" not in str(result)


def test_super_admin_corrects_archived_history_without_enabling_new_entries(api, seed_transaction, balance):
    transaction_id = seed_transaction(money=5000)
    assert api("PATCH", "/api/funds/1/archive", "root").status_code == 200
    assert api("PUT", f"/api/transactions/{transaction_id}", "root", {"money": 4000}).status_code == 200
    assert balance(1) == 4000
    assert api("PUT", f"/api/transactions/{transaction_id}/edit", data={"money": 3000}).status_code == 409
    assert api("POST", "/api/transactions/add", "root", {"fund_id": 1, "money": 100,
        "type": "income", "pay_type": "Kaspi"}).status_code == 409
    assert api("DELETE", f"/api/transactions/{transaction_id}", "root").status_code == 204
    assert balance(1) == 0


def test_income_edit_to_expense_or_other_owned_fund_reconciles_balances(api, seed_transaction, balance):
    transaction_id = seed_transaction(money=500)
    assert api("PUT", f"/api/transactions/{transaction_id}/edit", data={"fund_id": 2, "money": 125}).status_code == 200
    assert (balance(1), balance(2)) == (0, 125)
    assert api("PUT", f"/api/transactions/{transaction_id}/edit", data={"type": "expense", "money": 75}).status_code == 200
    assert (balance(1), balance(2)) == (0, -75)
