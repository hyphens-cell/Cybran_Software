"""Серверный финансовый интерфейс с учётом ролей."""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from io import BytesIO

from flask import Blueprint, abort, flash, g, redirect, render_template, request, send_file, session, url_for

from . import services as svc
from .auth import login_required, roles_required

bp = Blueprint("web", __name__)
ROLES = ("Super Admin", "Admin", "Cashier", "Investor")
TYPE_LABELS = {"income": "Доход", "expense": "Расход", "inter-transaction": "Перевод"}


def filters():
    return {key: request.args.get(key, "").strip() for key in ("date_from", "date_to", "type", "pay_type", "fund_id")}


def minor_units(value):
    """Преобразовать десятичную сумму из формы в точные минорные единицы."""
    try:
        amount = Decimal(str(value).strip().replace(" ", "").replace(",", "."))
        if not amount.is_finite() or amount <= 0 or amount > Decimal("92233720368547758.07"):
            raise ValueError
        # Сначала проверяем исходные цифры, чтобы контекст Decimal не округлил их
        # до проверки допустимой точности.
        parts = amount.as_tuple()
        subcent_digits = max(0, -parts.exponent - 2)
        if subcent_digits and any(parts.digits[-subcent_digits:]):
            raise ValueError
        result = amount * 100
        if result != result.to_integral_value():
            raise ValueError
        return int(result)
    except (InvalidOperation, ValueError, TypeError):
        raise svc.DomainError("Введите положительную сумму, не более двух знаков после запятой.")


def transaction_data():
    data = request.form.to_dict()
    data["money"] = minor_units(data.get("amount", ""))
    if not data.get("name"):
        data["name"] = TYPE_LABELS.get(data.get("type"), "Межфондовый перевод")
    if not data.get("datetime"):
        data.pop("datetime", None)
    return data


def form_error(exc):
    flash(str(exc), "danger")
    return getattr(exc, "status", 400)


@bp.app_context_processor
def presentation_context():
    return {"role_labels": {"Super Admin": "Супер-администратор", "Admin": "Администратор", "Cashier": "Кассир", "Investor": "Инвестор"},
            "type_labels": TYPE_LABELS, "roles": ROLES, "today": datetime.now(timezone.utc).date().isoformat(), "can_modify": svc.can_modify}


@bp.route("/")
@login_required
def index():
    if g.user["role"] in ("Super Admin", "Investor"):
        return redirect(url_for("web.dashboard"))
    if g.user["role"] == "Cashier":
        return redirect(url_for("web.cashier"))
    return redirect(url_for("web.funds"))


@bp.route("/dashboard")
@roles_required("Super Admin", "Investor")
def dashboard():
    selected = filters()
    data = svc.dashboard(g.user, selected)
    colors = ["#d63837", "#242b38", "#8998a6", "#cfaa79", "#c7cdd4", "#b65859"]
    positive = [item for item in data["distribution"] if item["balance"] > 0]
    total = sum(item["balance"] for item in positive)
    segments, start = [], 0
    for i, item in enumerate(data["distribution"]):
        if item["balance"] <= 0:
            continue
        end = start + item["balance"] * 36000 // total
        segments.append(f"{colors[i % len(colors)]} {start // 100}.{start % 100:02d}deg {end // 100}.{end % 100:02d}deg")
        start = end
    gradient = ", ".join(segments) or "#e8eaee 0deg 360deg"
    peak = max((item["money"] for item in data["trend"]), default=0) or 1
    chart = [{**item, "height": max(2, item["money"] * 148 // peak)} for item in data["trend"]]
    accessible = {fund["id"] for fund in svc.list_funds(g.user)}
    return render_template("dashboard.html", data=data, filters=selected, colors=colors,
                           gradient=gradient, chart=chart, accessible=accessible)


@bp.route("/reports/export")
@roles_required("Super Admin", "Investor")
def export():
    content, mime, filename = svc.export_file(g.user, filters(), request.args.get("format", "csv"))
    return send_file(BytesIO(content), mimetype=mime, as_attachment=True, download_name=filename)


@bp.route("/funds")
@login_required
def funds():
    items = svc.list_funds(g.user)
    return render_template("funds.html", funds=items, total=sum(item["balance"] for item in items))


@bp.route("/funds/<int:fund_id>")
@login_required
def fund_detail(fund_id):
    fund = svc.fund_detail(g.user, fund_id)
    selected = filters()
    selected["fund_id"] = str(fund_id)
    transactions = svc.list_transactions(g.user, selected)
    return render_template("fund_detail.html", fund=fund, transactions=transactions, filters=selected,
                           funds=[fund], last_id=svc.last_cashier_transaction_id(g.user) if g.user["role"] == "Cashier" else None)


@bp.route("/funds/new", methods=["GET", "POST"])
@bp.route("/funds/<int:fund_id>/edit", methods=["GET", "POST"])
@roles_required("Super Admin")
def fund_form(fund_id=None):
    fund = svc.fund_detail(g.user, fund_id) if fund_id else {}
    status = 200
    if request.method == "POST":
        try:
            if fund_id:
                svc.edit_fund(g.user, fund_id, request.form.to_dict())
            else:
                svc.create_fund(g.user, request.form.to_dict())
            flash("Фонд сохранён.", "success")
            return redirect(url_for("web.funds"))
        except svc.DomainError as exc:
            status = form_error(exc)
    return render_template("fund_form.html", fund=fund, values=request.form if request.method == "POST" else fund), status


@bp.post("/funds/<int:fund_id>/archive")
@roles_required("Super Admin")
def fund_archive(fund_id):
    svc.archive_fund(g.user, fund_id)
    flash("Фонд архивирован. История операций сохранена.", "success")
    return redirect(url_for("web.funds"))


@bp.route("/transactions")
@login_required
def transactions():
    selected = filters()
    return render_template("transactions.html", transactions=svc.list_transactions(g.user, selected),
                           funds=svc.list_funds(g.user), filters=selected,
                           last_id=svc.last_cashier_transaction_id(g.user) if g.user["role"] == "Cashier" else None)


@bp.route("/transactions/new", methods=["GET", "POST"])
@roles_required("Super Admin", "Admin", "Cashier")
def transaction_new():
    status = 200
    values = request.form if request.method == "POST" else {"type": request.args.get("type", "income"), "fund_id": request.args.get("fund_id", "")}
    if request.method == "POST":
        try:
            svc.create_transaction(g.user, transaction_data())
            flash("Операция проведена. Баланс фонда обновлён.", "success")
            return redirect(url_for("web.cashier" if g.user["role"] == "Cashier" else "web.transactions"))
        except svc.DomainError as exc:
            status = form_error(exc)
    return render_template("transaction_form.html", values=values, funds=svc.list_funds(g.user, include_archived=False), transaction=None, transfer=False), status


@bp.route("/transfers/new", methods=["GET", "POST"])
@roles_required("Super Admin", "Admin")
def transfer_new():
    status = 200
    if request.method == "POST":
        try:
            svc.create_transfer(g.user, transaction_data())
            flash("Перевод проведён. Балансы обоих фондов обновлены.", "success")
            return redirect(url_for("web.transactions"))
        except svc.DomainError as exc:
            status = form_error(exc)
    return render_template("transaction_form.html", values=request.form, funds=svc.list_funds(g.user, include_archived=False), transaction=None, transfer=True), status


@bp.route("/transactions/<int:transaction_id>/edit", methods=["GET", "POST"])
@roles_required("Super Admin", "Admin")
def transaction_edit(transaction_id):
    transaction = svc.transaction_for_modify(g.user, transaction_id)
    status = 200
    transfer = transaction["type"] == "inter-transaction"
    values = dict(transaction)
    values["amount"] = f"{transaction['money'] // 100}.{transaction['money'] % 100:02d}"
    values["fund_id"] = transaction["to_fund_id"] if transaction["type"] == "income" else transaction["from_fund_id"]
    if request.method == "POST":
        values = request.form
        try:
            svc.edit_transaction(g.user, transaction_id, transaction_data())
            flash("Изменения сохранены. Балансы пересчитаны.", "success")
            return redirect(url_for("web.transactions"))
        except svc.DomainError as exc:
            status = form_error(exc)
    return render_template("transaction_form.html", values=values, funds=svc.list_funds(g.user), transaction=transaction, transfer=transfer), status


@bp.post("/transactions/<int:transaction_id>/delete")
@roles_required("Super Admin", "Admin")
def transaction_delete(transaction_id):
    svc.delete_transaction(g.user, transaction_id)
    flash("Ошибочная операция удалена. Балансы пересчитаны.", "success")
    return redirect(url_for("web.transactions"))


@bp.route("/cashier", methods=["GET", "POST"])
@roles_required("Cashier", "Super Admin")
def cashier():
    status = 200
    if request.method == "POST":
        try:
            data = transaction_data()
            data["type"] = "income"
            data["name"] = "Приём оплаты"
            svc.create_transaction(g.user, data)
            flash("Оплата принята. Операция сохранена.", "success")
            return redirect(url_for("web.cashier"))
        except svc.DomainError as exc:
            status = form_error(exc)
    selected = {"date_from": datetime.now(timezone.utc).date().isoformat(), "date_to": datetime.now(timezone.utc).date().isoformat()}
    items = svc.list_transactions(g.user, selected)
    return render_template("cashier.html", funds=svc.list_funds(g.user, include_archived=False),
                           values=request.form, transactions=items, last_id=svc.last_cashier_transaction_id(g.user),
                           shift_income=sum(item["money"] for item in items if item["type"] == "income" and item["user_id"] == g.user["id"])), status


@bp.route("/shifts")
@roles_required("Cashier", "Super Admin")
def shifts():
    selected = filters()
    items = svc.list_transactions(g.user, selected)
    groups = {}
    own_days = {item["datetime"][:10] for item in items if item["user_id"] == g.user["id"]}
    for item in items:
        day = item["datetime"][:10]
        if day not in own_days:
            continue
        group = groups.setdefault(day, {"date": day, "transactions": [], "income": 0, "expense": 0})
        group["transactions"].append(item)
        if item["type"] in ("income", "expense") and item["user_id"] == g.user["id"]:
            group[item["type"]] += item["money"]
    return render_template("shifts.html", groups=list(groups.values()), filters=selected,
                           funds=svc.list_funds(g.user), last_id=svc.last_cashier_transaction_id(g.user))


@bp.post("/transactions/<int:transaction_id>/cancel")
@roles_required("Cashier", "Super Admin")
def transaction_cancel(transaction_id):
    svc.cancel_last(g.user, transaction_id)
    flash("Последняя ошибочная операция отменена.", "success")
    return redirect(url_for("web.cashier"))


@bp.route("/users")
@roles_required("Super Admin")
def users():
    search, role = request.args.get("search", ""), request.args.get("role", "")
    return render_template("users.html", users=svc.list_users(g.user, search, role), search=search, role=role)


@bp.route("/users/new", methods=["GET", "POST"])
@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@roles_required("Super Admin")
def user_form(user_id=None):
    user = next((item for item in svc.list_users(g.user) if item["id"] == user_id), None) if user_id else None
    if user_id and not user:
        abort(404)
    status = 200
    if request.method == "POST":
        try:
            if user_id:
                svc.edit_user(g.user, user_id, request.form.to_dict())
            else:
                svc.create_user(g.user, request.form.to_dict())
            flash("Пользователь сохранён.", "success")
            return redirect(url_for("web.users"))
        except svc.DomainError as exc:
            status = form_error(exc)
    return render_template("user_form.html", user=user, values=request.form if request.method == "POST" else (user or {})), status


@bp.post("/users/<int:user_id>/block")
@roles_required("Super Admin")
def user_block(user_id):
    value = request.form.get("is_active")
    if value not in ("0", "1"):
        raise svc.DomainError("Статус пользователя должен быть явно указан: 0 или 1.")
    svc.block_user(g.user, user_id, value == "1")
    flash("Статус пользователя изменён.", "success")
    return redirect(url_for("web.users"))


@bp.post("/users/<int:user_id>/password")
@roles_required("Super Admin")
def user_password(user_id):
    svc.reset_password(g.user, user_id, request.form.get("password", ""))
    flash("Пароль пользователя изменён.", "success")
    return redirect(url_for("web.user_form", user_id=user_id))


@bp.route("/rights", methods=["GET", "POST"])
@roles_required("Super Admin")
def rights():
    status = 200
    if request.method == "POST":
        try:
            svc.set_rights(g.user, request.form.get("user_id"), request.form.getlist("fund_ids"))
            flash("Права доступа сохранены.", "success")
            return redirect(url_for("web.rights", user_id=request.form.get("user_id")))
        except svc.DomainError as exc:
            status = form_error(exc)
    users = svc.list_users(g.user)
    selected_id = request.values.get("user_id", str(users[0]["id"]) if users else "")
    selected = next((item for item in users if str(item["id"]) == selected_id), None)
    assigned = {item["fund_id"] for item in svc.list_rights(g.user) if str(item["user_id"]) == selected_id}
    return render_template("rights.html", users=users, selected=selected, funds=svc.list_funds(g.user), assigned=assigned), status


@bp.route("/tokens", methods=["GET", "POST"])
@roles_required("Super Admin")
def tokens():
    token, status = None, 200
    if request.method == "POST":
        try:
            token = svc.create_token(g.user, request.form.get("user_id"))
        except svc.DomainError as exc:
            status = form_error(exc)
    response = render_template("tokens.html", tokens=svc.list_tokens(g.user), users=svc.list_users(g.user), generated=token)
    return response, status, {"Cache-Control": "no-store"}


@bp.post("/tokens/<int:token_id>/revoke")
@roles_required("Super Admin")
def token_revoke(token_id):
    svc.revoke_token(g.user, token_id)
    flash("API-токен отозван.", "success")
    return redirect(url_for("web.tokens"))


@bp.get("/sessions")
@roles_required("Super Admin")
def web_sessions():
    return render_template("sessions.html", sessions=svc.list_web_sessions(g.user),
                           current_session_id=g.web_session_id)


@bp.post("/sessions/<int:session_id>/revoke")
@roles_required("Super Admin")
def web_session_revoke(session_id):
    svc.revoke_web_session(g.user, session_id)
    if session_id == g.web_session_id:
        session.clear()
        return redirect(url_for("auth.login", ended="1"))
    flash("Сессия пользователя завершена.", "success")
    return redirect(url_for("web.web_sessions"))


@bp.post("/sessions/revoke-all")
@roles_required("Super Admin")
def web_sessions_revoke_all():
    keep_current = request.form.get("scope") == "others"
    count = svc.revoke_all_web_sessions(g.user, g.web_session_id if keep_current else None)
    if not keep_current:
        session.clear()
        return redirect(url_for("auth.login", ended="all"))
    flash(f"Завершено сессий: {count}.", "success")
    return redirect(url_for("web.web_sessions"))
