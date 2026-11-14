import secrets
from functools import wraps
from flask import session, request, g, abort
from models import usuario


def csrf():
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def install(app):
    @app.before_request
    def protect():
        g.user = None
        if session.get("user_id"):
            row = usuario.find(session["user_id"])
            if row and row["ativo"]:
                g.user = row
            else:
                session.clear()
        if request.path.startswith("/api/") and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            expected = session.get("csrf")
            supplied = request.headers.get("X-CSRF-Token", "")
            if not expected or not secrets.compare_digest(expected, supplied):
                abort(403, description="Token CSRF invalido. Atualize a pagina.")


def role(*roles):
    def decorate(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not g.user:
                abort(401, description="Entre para continuar.")
            if roles and g.user["cargo"] not in roles:
                abort(403, description="Acesso negado.")
            return fn(*args, **kwargs)
        return wrapped
    return decorate
