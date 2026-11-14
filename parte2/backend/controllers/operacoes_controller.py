from flask import g
from controllers.auth import body
from services import operacoes
from utils.security import role


@role('cliente','cozinheiro','administrador')
def benches():
    return operacoes.benches(g.user)


@role('administrador')
def add_bench():
    return operacoes.add_bench(g.user, body())


@role('administrador')
def update_bench(bid):
    return operacoes.update_bench(g.user, bid, body())


@role('cliente','administrador')
def list_reservations():
    return operacoes.list_reservations(g.user)


@role('cliente')
def reserve():
    return operacoes.reserve(g.user, body())


@role('cliente','administrador')
def cancel(aid):
    return operacoes.cancel(g.user, aid)


@role('administrador')
def payments():
    return operacoes.payments(g.user)


@role('administrador')
def pay(vid):
    return operacoes.pay(g.user, vid, body())


@role('administrador')
def reports():
    return operacoes.reports(g.user)
