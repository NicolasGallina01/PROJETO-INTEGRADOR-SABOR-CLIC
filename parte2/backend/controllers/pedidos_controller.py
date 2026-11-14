from flask import g
from controllers.auth import body
from services import pedidos
from utils.security import role



@role("cliente", "cozinheiro", "administrador")
def list_orders():
    return pedidos.list_for(g.user)


@role("cliente")
def create_order():
    return pedidos.create(g.user, body()), 201


@role("cozinheiro", "administrador")
def status(pid):
    return pedidos.change_status(g.user, pid, body().get("status"))


@role("cozinheiro", "administrador")
def time(pid):
    return pedidos.change_time(g.user, pid, body().get("tempo_estimado"))
