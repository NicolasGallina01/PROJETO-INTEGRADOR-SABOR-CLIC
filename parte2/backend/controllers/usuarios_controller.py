from flask import abort, g
from controllers import auth
from models import usuario
from models.base import execute
from services.usuarios import create
from database import transaction
from utils.security import role



@role("administrador")
def users():
    return [usuario.public(row) for row in usuario.all_users()]


@role("administrador")
def add_user():
    return {"usuario": create(auth.body())}, 201


@role("administrador")
def active(uid):
    data = auth.body()
    if not isinstance(data.get("ativo"), bool):
        abort(400, description="ativo deve ser booleano.")
    if uid == g.user["id_usuario"] and not data["ativo"]:
        abort(409, description="Nao desative sua propria conta.")
    if not usuario.find(uid):
        abort(404)
    with transaction():
        execute("UPDATE Usuario SET ativo=%s WHERE id_usuario=%s", (data["ativo"], uid))
    return usuario.public(usuario.find(uid))
