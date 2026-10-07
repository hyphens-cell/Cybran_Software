"""Explicit sample data for a separate local demonstration database."""
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click
from flask import current_app

from . import services as svc
from .db import atomic, get_db


def seed_demo():
    db = get_db()
    if db.execute('SELECT count(*) FROM Users').fetchone()[0]:
        raise click.ClickException('Demo seed requires an empty database; existing data has not been changed.')
    passwords = {name:secrets.token_urlsafe(15) for name in ('superadmin','admin','cashier','investor')}
    with atomic():
        db.execute('INSERT INTO Users(username,fullname,password_hash,role) VALUES(?,?,?,?)',
                   ('superadmin','Системный администратор',svc.password_hash(passwords['superadmin']),'Super Admin'))
        sa = dict(db.execute("SELECT * FROM Users WHERE username='superadmin'").fetchone())
        users = {'superadmin':sa}
        for name, fullname, role in [('admin','Администратор фондов','Admin'),('cashier','Кассир','Cashier'),('investor','Инвестор','Investor')]:
            users[name] = svc.create_user(sa,dict(username=name,fullname=fullname,role=role,password=passwords[name]))
        funds = []
        for name, description, kind in [('Основная касса','Ежедневные поступления и операционные расходы','for_stats'),
              ('Разработка','Финансы проектов разработки','for_stats'),('Маркетинг','Продвижение и рекламные кампании','for_stats'),
              ('Технический фонд','Тестовые операции, исключённые из сводной отчётности','no_stats')]:
            funds.append(svc.create_fund(sa,dict(name=name,description=description,type=kind)))
        for name in ('admin','cashier','investor'):
            svc.set_rights(sa,users[name]['id'],[funds[0]['id'],funds[1]['id']])
        now = datetime.now(timezone.utc)
        for offset in range(6,-1,-1):
            when = (now-timedelta(days=offset)).replace(hour=10,minute=30,second=0).isoformat()
            for fund_index, base in ((0,1820000),(1,960000)):
                svc.create_transaction(users['cashier'], dict(name='Оплата услуг',description='Демонстрационная операция',
                    money=base+offset*73100,type='income',pay_type=('Kaspi','Карта','Наличные')[offset%3],
                    fund_id=funds[fund_index]['id'],datetime=when))
            svc.create_transaction(users['admin'],dict(name='Операционные расходы',description='Демонстрационная операция',
                money=360000+offset*8100,type='expense',pay_type='Карта',fund_id=funds[0]['id'],datetime=when))
        svc.create_transaction(sa,dict(name='Бюджет продвижения',money=4500000,type='income',pay_type='Карта',fund_id=funds[2]['id']))
        svc.create_transaction(sa,dict(name='Рекламная кампания',money=980000,type='expense',pay_type='Карта',fund_id=funds[2]['id']))
        svc.create_transaction(sa,dict(name='Тестовое поступление',money=50000,type='income',pay_type='Наличные',fund_id=funds[3]['id']))
        svc.create_transfer(users['admin'],dict(name='Финансирование разработки',description='Перераспределение средств',money=1800000,
            from_fund_id=funds[0]['id'],to_fund_id=funds[1]['id']))
    path = Path(current_app.instance_path)/'demo-access.txt'
    path.write_text('ДЕМО Cybran Software — только локальные тестовые данные\n\n'+
                    '\n'.join(f'{name}: {password}' for name,password in passwords.items())+'\n',encoding='utf-8')
    click.echo(f'Demo created. Local credentials: {path}')
