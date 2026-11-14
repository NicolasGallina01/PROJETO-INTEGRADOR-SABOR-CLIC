from flask import Flask
from config import Config
from database import init_app as init_database
from routes.health import health_bp
from utils.errors import register_error_handlers
from routes.auth import bp as auth_bp
from routes.catalogo import bp as catalogo_bp
from routes.estoque import bp as estoque_bp
from routes.pedidos import bp as pedidos_bp
from routes.operacoes import bp as operacoes_bp
from utils.security import install
import click
from services.usuarios import create


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    app.json.ensure_ascii = False
    init_database(app)
    register_error_handlers(app)
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(catalogo_bp, url_prefix="/api")
    app.register_blueprint(estoque_bp, url_prefix="/api")
    app.register_blueprint(pedidos_bp, url_prefix="/api")
    app.register_blueprint(operacoes_bp, url_prefix="/api")
    install(app)
    from routes.pages import bp as pages_bp
    app.register_blueprint(pages_bp)

    @app.cli.command("create-admin")
    @click.option("--nome", prompt=True)
    @click.option("--email", prompt=True)
    @click.password_option()
    def create_admin(nome, email, password):
        create({"nome": nome, "email": email, "senha": password, "cargo": "administrador"})
        click.echo("Administrador criado.")
    return app


if __name__ == "__main__":
    create_app().run()
