from flask import Blueprint
from controllers import pedidos_controller as controller

bp = Blueprint("pedidos", __name__)
bp.add_url_rule("/pedidos", view_func=controller.list_orders, methods=["GET"])
bp.add_url_rule("/pedidos", view_func=controller.create_order, methods=["POST"])
bp.add_url_rule("/pedidos/<int:pid>/status", view_func=controller.status, methods=["PATCH"])
bp.add_url_rule("/pedidos/<int:pid>/tempo", view_func=controller.time, methods=["PATCH"])
