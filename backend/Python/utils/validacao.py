import re


def validar_email(email):

    if not email:
        return False

    return bool(
        re.match(
            r"^[^@]+@[^@]+\.[^@]+$",
            email
        )
    )


def validar_senha(senha):

    if not senha or len(senha) < 8:
        return False

    if not re.search(r"[A-Z]", senha):
        return False

    if not re.search(r"[0-9]", senha):
        return False

    if not re.search(r"[^a-zA-Z0-9]", senha):
        return False

    return True


def validar_nome(nome):

    if not nome:
        return False

    if len(nome.strip()) < 3:
        return False

    return True