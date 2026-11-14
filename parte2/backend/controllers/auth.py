import secrets
from flask import request, session, g, abort, flash, get_flashed_messages
from werkzeug.security import check_password_hash, generate_password_hash
from models import usuario
from services.usuarios import create
from utils.security import csrf

DUMMY_HASH = generate_password_hash(secrets.token_urlsafe(32))


def body():
    data = request.get_json()
    if not isinstance(data, dict):
        abort(400, description="Envie um objeto JSON.")
    return data


def me():
    return {"usuario": usuario.public(g.user) if g.user else None, "csrf": csrf(),
            "mensagens": get_flashed_messages(with_categories=True)}


def login():
    data = body()
    email = data.get("email", "")
    senha = data.get("senha", "")
    if not isinstance(email, str) or not isinstance(senha, str) or len(senha) > 128:
        abort(400, description="Credenciais invalidas.")
    row = usuario.by_email(email.strip().lower())
    valid = check_password_hash(row["senha_hash"] if row else DUMMY_HASH, senha)
    if not row or not valid or not row["ativo"]:
        abort(401, description="Email ou senha invalidos.")
    session.clear()
    session["user_id"] = row["id_usuario"]
    flash("Login realizado.", "sucesso")
    g.user = row
    return me()


def register():
    user = create(body(), public=True)
    flash("Conta criada.", "sucesso")
    return {"usuario": user, "mensagens": get_flashed_messages(with_categories=True)}, 201


def logout():
    session.clear()
    flash("Sessao encerrada.", "sucesso")
    return {"ok": True, "csrf": csrf(), "mensagens": get_flashed_messages(with_categories=True)}
