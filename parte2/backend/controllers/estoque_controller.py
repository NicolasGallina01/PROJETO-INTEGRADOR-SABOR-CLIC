from flask import abort
from controllers.auth import body
from services import estoque
from database import transaction
from models.base import execute
from utils.security import role



@role("administrador")
def list_ingredients():
    return estoque.list_all()


@role("administrador")
def create_ingredient():
    return estoque.create(body()), 201


@role("administrador")
def update_ingredient(iid):
    return estoque.update(iid, body())


@role("administrador")
def list_substitutions(iid):
    return estoque.substitutions(iid)


@role("administrador")
def add_substitution(iid):
    return estoque.add_substitution(iid, body()), 201


@role("administrador")
def remove_substitution(iid, sid):
    with transaction():
        _, count = execute("DELETE FROM Substituicao_Ingrediente WHERE id_ingrediente_principal=%s AND id_ingrediente_substituto=%s", (iid, sid))
        if not count:
            abort(404)
    return {"ok": True}
