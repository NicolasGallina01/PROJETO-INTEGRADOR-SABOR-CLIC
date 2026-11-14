from flask import Blueprint
from controllers import operacoes_controller as controller

bp = Blueprint('operacoes', __name__)
bp.add_url_rule('/bancadas', view_func=controller.benches, methods=['GET'])
bp.add_url_rule('/bancadas', view_func=controller.add_bench, methods=['POST'])
bp.add_url_rule('/bancadas/<int:bid>', view_func=controller.update_bench, methods=['PATCH'])
bp.add_url_rule('/agendamentos', view_func=controller.list_reservations, methods=['GET'])
bp.add_url_rule('/agendamentos', view_func=controller.reserve, methods=['POST'])
bp.add_url_rule('/agendamentos/<int:aid>/cancelar', view_func=controller.cancel, methods=['PATCH'])
bp.add_url_rule('/pagamentos', view_func=controller.payments, methods=['GET'])
bp.add_url_rule('/pagamentos/<int:vid>/confirmar', view_func=controller.pay, methods=['PATCH'])
bp.add_url_rule('/relatorios', view_func=controller.reports, methods=['GET'])
