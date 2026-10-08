"""Имена endpoint и разрешённые роли взяты непосредственно со страниц 8–9 ТЗ."""
from functools import wraps

from flask import Blueprint, g, jsonify, request

from .auth import authenticate_api
from . import services as svc

bp = Blueprint('api', __name__, url_prefix='/api')
bp.before_request(authenticate_api)


def roles(*allowed):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            svc.require_role(g.user, 'Super Admin', *allowed)
            return view(*args, **kwargs)
        return wrapped
    return decorator


def body():
    if not request.is_json:
        raise svc.DomainError('Требуется Content-Type: application/json.',415)
    data = request.get_json()
    if not isinstance(data,dict):
        raise svc.DomainError('Тело запроса должно быть JSON-объектом.')
    return data


@bp.post('/create_user')
@roles()
def create_user():
    return jsonify(svc.create_user(g.user,body())),201


@bp.put('/users/<int:user_id>/edit_user')
@roles()
def edit_user(user_id):
    return jsonify(svc.edit_user(g.user,user_id,body()))


@bp.patch('/users/<int:user_id>/block')
@roles()
def block_user(user_id):
    return jsonify(svc.block_user(g.user,user_id,body().get('is_active')))


@bp.post('/create_fund')
@roles()
def create_fund():
    return jsonify(svc.create_fund(g.user,body())),201


@bp.patch('/funds/<int:fund_id>/archive')
@roles()
def archive_fund(fund_id):
    return jsonify(svc.archive_fund(g.user,fund_id))


@bp.post('/rights')
@roles()
def grant_right():
    data = body()
    return jsonify(svc.grant_right(g.user,svc.identifier(data.get('user_id')),svc.identifier(data.get('fund_id')))),201


@bp.delete('/rights/<int:user_id>/<int:fund_id>')
@roles()
def revoke_right(user_id,fund_id):
    svc.revoke_right(g.user,user_id,fund_id)
    return '',204


@bp.delete('/tokens/<int:token_id>')
@roles()
def revoke_token(token_id):
    svc.revoke_token(g.user,token_id)
    return '',204


@bp.put('/transactions/<int:transaction_id>')
@roles()
def global_edit(transaction_id):
    return jsonify(svc.edit_transaction(g.user,transaction_id,body()))


@bp.delete('/transactions/<int:transaction_id>')
@roles()
def global_delete(transaction_id):
    svc.delete_transaction(g.user,transaction_id)
    return '',204


@bp.get('/funds')
@roles('Admin')
def funds():
    return jsonify(svc.list_funds(g.user))


@bp.post('/transactions/add')
@roles('Admin')
def add():
    return jsonify(svc.create_transaction(g.user,body())),201


@bp.post('/transactions/add_transfer')
@roles('Admin')
def transfer():
    return jsonify(svc.create_transfer(g.user,body())),201


@bp.get('/transactions')
@roles('Admin')
def transactions():
    return jsonify(svc.list_transactions(g.user,request.args))


@bp.put('/transactions/<int:transaction_id>/edit')
@roles('Admin')
def edit(transaction_id):
    return jsonify(svc.edit_transaction(g.user,transaction_id,body()))


@bp.delete('/transactions/<int:transaction_id>/delete')
@roles('Admin')
def delete(transaction_id):
    svc.delete_transaction(g.user,transaction_id)
    return '',204
