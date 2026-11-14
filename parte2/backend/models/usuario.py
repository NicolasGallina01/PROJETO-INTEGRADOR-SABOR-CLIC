from models.base import fetch_one, fetch_all

SELECT = """SELECT u.*, CASE WHEN a.id_usuario IS NOT NULL THEN 'administrador'
 WHEN c.id_usuario IS NOT NULL THEN 'cozinheiro' ELSE 'cliente' END AS cargo
 FROM Usuario u LEFT JOIN Administrador a USING(id_usuario)
 LEFT JOIN Cozinheiro c USING(id_usuario)"""


def find(user_id):
    return fetch_one(SELECT + " WHERE u.id_usuario=%s", (user_id,))


def by_email(email):
    return fetch_one(SELECT + " WHERE u.email=%s", (email,))


def all_users():
    return fetch_all(SELECT + " ORDER BY u.id_usuario")


def public(row):
    return {"id": row["id_usuario"], "nome": row["nome"], "email": row["email"],
            "cargo": row["cargo"], "ativo": bool(row["ativo"])}
