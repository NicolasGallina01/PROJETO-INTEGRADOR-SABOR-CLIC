from database import cursor


def check_database():
    with cursor() as db_cursor:
        db_cursor.execute("SELECT 1 AS ok")
        return db_cursor.fetchone()["ok"] == 1
