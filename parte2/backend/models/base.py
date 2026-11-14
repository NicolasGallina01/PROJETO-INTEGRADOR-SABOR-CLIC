from database import cursor


def fetch_one(sql, params=()):
    with cursor() as db_cursor:
        db_cursor.execute(sql, params)
        return db_cursor.fetchone()


def fetch_all(sql, params=()):
    with cursor() as db_cursor:
        db_cursor.execute(sql, params)
        return db_cursor.fetchall()


def execute(sql, params=()):
    """Executar mutacoes dentro de database.transaction()."""
    from flask import g
    if not g.get("transaction_active", False):
        raise RuntimeError("Mutacoes exigem uma transacao explicita.")
    with cursor() as db_cursor:
        db_cursor.execute(sql, params)
        return db_cursor.lastrowid, db_cursor.rowcount
