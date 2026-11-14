from flask import Blueprint
from controllers import catalogo_controller as controller

bp = Blueprint("catalogo", __name__)
bp.add_url_rule("/pratos", view_func=controller.dishes, methods=["GET"])
bp.add_url_rule("/pratos", view_func=controller.create, methods=["POST"])
bp.add_url_rule("/pratos/<int:pid>", view_func=controller.update, methods=["PUT"])
bp.add_url_rule("/pratos/<int:pid>", view_func=controller.remove, methods=["DELETE"])
bp.add_url_rule("/pratos/<int:pid>/ficha", view_func=controller.recipe, methods=["GET"])
bp.add_url_rule("/pratos/<int:pid>/ficha", view_func=controller.save_recipe, methods=["PUT"])


