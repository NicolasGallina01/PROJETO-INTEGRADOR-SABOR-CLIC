import re
from flask import abort
from werkzeug.security import generate_password_hash
from database import transaction
from models.base import execute
from models import usuario


def text(data, key, limit, required=True):
    value = data.get(key, "")
    if not isinstance(value, str) or len(value.strip()) > limit or (required and not value.strip()):
        abort(400, description=f"Campo {key} invalido.")
    return value.strip()


def create(data, public=False):
    nome = text(data, "nome", 60)
    email = text(data, "email", 80).lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        abort(400, description="Email invalido.")
    senha = data.get("senha", "")
    if not isinstance(senha, str) or not 8 <= len(senha) <= 128:
        abort(400, description="A senha deve ter entre 8 e 128 caracteres.")
    cargo = "cliente" if public else data.get("cargo", "cliente")
    if cargo not in {"cliente", "cozinheiro", "administrador"}:
        abort(400, description="Perfil invalido.")
    turno = data.get("turno", "MANHA")
    if not isinstance(turno, str):
        abort(400, description="Turno invalido.")
    turno = turno.upper()
    especialidade = text(data, "especialidade", 30, False)
    if cargo == "cozinheiro" and (turno not in {"MANHA", "TARDE", "NOITE"} or not especialidade):
        abort(400, description="Informe turno e especialidade validos.")
    with transaction():
        uid, _ = execute("INSERT INTO Usuario (nome,email,senha_hash) VALUES (%s,%s,%s)",
                         (nome, email, generate_password_hash(senha)))
        if cargo == "cliente":
            execute("INSERT INTO Cliente (id_usuario,logradouro) VALUES (%s,%s)",
                    (uid, text(data, "endereco", 80, False)))
        elif cargo == "administrador":
            execute("INSERT INTO Administrador (id_usuario,nivel_permissao) VALUES (%s,1)", (uid,))
        else:
            execute("INSERT INTO Cozinheiro (id_usuario,turno,especialidade) VALUES (%s,%s,%s)",
                    (uid, turno, especialidade))
    return usuario.public(usuario.find(uid))
