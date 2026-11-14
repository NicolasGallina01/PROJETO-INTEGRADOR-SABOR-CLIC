from flask import Blueprint
from controllers import pages_controller as controller

bp = Blueprint('pages', __name__)
bp.add_url_rule('/', view_func=controller.index)
bp.add_url_rule('/<page>.html', view_func=controller.page)
bp.add_url_rule('/script/<path:name>', view_func=controller.script)
bp.add_url_rule('/style/<path:name>', view_func=controller.style)
bp.add_url_rule('/<name>.js', view_func=controller.root_script)
bp.add_url_rule('/style.css', view_func=controller.root_style)
