from flask import Blueprint
from controllers import usuarios_controller as controller
from controllers import auth

bp = Blueprint("auth", __name__)
bp.add_url_rule("/auth/me", view_func=auth.me, methods=["GET"])
bp.add_url_rule("/auth/login", view_func=auth.login, methods=["POST"])
bp.add_url_rule("/auth/registro", view_func=auth.register, methods=["POST"])
bp.add_url_rule("/auth/logout", view_func=auth.logout, methods=["POST"])
bp.add_url_rule("/usuarios", view_func=controller.users, methods=["GET"])
bp.add_url_rule("/usuarios", view_func=controller.add_user, methods=["POST"])
bp.add_url_rule("/usuarios/<int:uid>", view_func=controller.active, methods=["PATCH"])
