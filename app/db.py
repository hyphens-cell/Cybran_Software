"""SQLite persistence. All monetary mutations use an explicit write transaction."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS Users (
 id INTEGER PRIMARY KEY,
 username TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK(length(username) BETWEEN 1 AND 50),
 fullname TEXT NOT NULL CHECK(length(fullname) BETWEEN 1 AND 150),
 password_hash TEXT NOT NULL CHECK(length(password_hash)<=256),
 role TEXT NOT NULL CHECK(role IN ('Super Admin','Admin','Cashier','Investor')),
 is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
 auth_version INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS Funds (
 id INTEGER PRIMARY KEY,
 name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 50),
 description TEXT NOT NULL DEFAULT '' CHECK(length(description)<=150),
 type TEXT NOT NULL CHECK(type IN ('for_stats','no_stats')),
 user_id INTEGER NOT NULL REFERENCES Users(id),
 is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1))
);
CREATE TABLE IF NOT EXISTS Rights (
 id INTEGER PRIMARY KEY,
 fund_id INTEGER NOT NULL REFERENCES Funds(id),
 user_id INTEGER NOT NULL REFERENCES Users(id),
 UNIQUE(user_id,fund_id)
);
CREATE TABLE IF NOT EXISTS ApiTokens (
 id INTEGER PRIMARY KEY,
 token TEXT NOT NULL UNIQUE CHECK(length(token)=64),
 active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
 datetime TEXT NOT NULL,
 user_id INTEGER NOT NULL REFERENCES Users(id)
);
CREATE TABLE IF NOT EXISTS Transactions (
 id INTEGER PRIMARY KEY,
 name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 50),
 description TEXT NOT NULL DEFAULT '' CHECK(length(description)<=150),
 money INTEGER NOT NULL CHECK(typeof(money)='integer' AND money>0),
 type TEXT NOT NULL CHECK(type IN ('income','expense','inter-transaction')),
 pay_type TEXT NOT NULL CHECK(length(pay_type) BETWEEN 1 AND 50),
 datetime TEXT NOT NULL,
 from_fund_id INTEGER REFERENCES Funds(id),
 to_fund_id INTEGER REFERENCES Funds(id),
 user_id INTEGER NOT NULL REFERENCES Users(id),
 transfer_id TEXT,
 transfer_side TEXT CHECK(transfer_side IN ('debit','credit')),
 UNIQUE(transfer_id,transfer_side),
 CHECK((type='income' AND from_fund_id IS NULL AND to_fund_id IS NOT NULL AND transfer_id IS NULL AND transfer_side IS NULL)
 OR (type='expense' AND from_fund_id IS NOT NULL AND to_fund_id IS NULL AND transfer_id IS NULL AND transfer_side IS NULL)
 OR (type='inter-transaction' AND from_fund_id IS NOT NULL AND to_fund_id IS NOT NULL
 AND from_fund_id != to_fund_id AND transfer_id IS NOT NULL AND transfer_side IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS ix_transactions_from ON Transactions(from_fund_id,datetime);
CREATE INDEX IF NOT EXISTS ix_transactions_to ON Transactions(to_fund_id,datetime);
CREATE INDEX IF NOT EXISTS ix_transactions_author ON Transactions(user_id,id);
CREATE INDEX IF NOT EXISTS ix_transactions_date ON Transactions(datetime);
CREATE INDEX IF NOT EXISTS ix_rights_fund ON Rights(fund_id);
"""


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'], isolation_level=None, timeout=15)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
        g.db.execute('PRAGMA busy_timeout=15000')
    return g.db


def init_db():
    Path(current_app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)
    get_db().executescript(SCHEMA)


def close_db(_error=None):
    connection = g.pop('db', None)
    if connection is not None:
        connection.close()


@contextmanager
def atomic():
    connection = get_db()
    if connection.in_transaction:
        yield connection
        return
    connection.execute('BEGIN IMMEDIATE')
    try:
        yield connection
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
