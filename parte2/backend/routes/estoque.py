from flask import Blueprint
from controllers import estoque_controller as controller

bp = Blueprint("estoque", __name__)
bp.add_url_rule("/ingredientes", view_func=controller.list_ingredients, methods=["GET"])
bp.add_url_rule("/ingredientes", view_func=controller.create_ingredient, methods=["POST"])
bp.add_url_rule("/ingredientes/<int:iid>", view_func=controller.update_ingredient, methods=["PATCH"])
bp.add_url_rule("/ingredientes/<int:iid>/substituicoes", view_func=controller.list_substitutions, methods=["GET"])
bp.add_url_rule("/ingredientes/<int:iid>/substituicoes", view_func=controller.add_substitution, methods=["POST"])
bp.add_url_rule("/ingredientes/<int:iid>/substituicoes/<int:sid>", view_func=controller.remove_substitution, methods=["DELETE"])
