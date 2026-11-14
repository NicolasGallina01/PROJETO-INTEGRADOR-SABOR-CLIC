from flask import Blueprint
from controllers.health_controller import health, readiness

health_bp = Blueprint("health", __name__)
health_bp.add_url_rule("/health", view_func=health, methods=["GET"])
health_bp.add_url_rule("/ready", view_func=readiness, methods=["GET"])
