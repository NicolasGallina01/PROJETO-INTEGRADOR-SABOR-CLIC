from flask import g
from controllers.auth import body
from services import catalogo
from database import transaction
from models.base import fetch_all, execute
from utils.security import role



@role()
def dishes():
    sql = "SELECT * FROM Prato"
    if g.user["cargo"] != "administrador":
        sql += " WHERE ativo=1"
    return [catalogo.public(row) for row in fetch_all(sql + " ORDER BY nome")]


@role("administrador")
def create():
    return catalogo.save(body()), 201


@role("administrador")
def update(pid):
    return catalogo.save(body(), pid)


@role("administrador")
def remove(pid):
    catalogo.dish(pid)
    with transaction():
        execute("UPDATE Prato SET ativo=0 WHERE id_prato=%s", (pid,))
    return {"ok": True}


@role("administrador")
def recipe(pid):
    catalogo.dish(pid)
    return [{"ingrediente_id": row["id_ingrediente"], "quantidade": float(row["quantidade_ingrediente"])}
            for row in fetch_all("SELECT * FROM Ficha_Tecnica WHERE id_prato=%s", (pid,))]


@role("administrador")
def save_recipe(pid):
    return catalogo.recipe(pid, body().get("ingredientes"))
