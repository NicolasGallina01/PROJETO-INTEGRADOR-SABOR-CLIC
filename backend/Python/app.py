from flask import Flask

from routes.usuarios import usuarios_bp
from routes.pratos import pratos_bp
from routes.pedidos import pedidos_bp
from routes.cozinhas import cozinhas_bp


app = Flask(__name__)

app.register_blueprint(usuarios_bp, url_prefix="/api/usuarios")
app.register_blueprint(pratos_bp, url_prefix="/api/pratos")
app.register_blueprint(pedidos_bp, url_prefix="/api/pedidos")
app.register_blueprint(cozinhas_bp, url_prefix="/api/cozinhas")


@app.route("/")
def inicio():
    return {
        "sistema": "Sabor & Clic",
        "status": "online"
    }


@app.route("/api")
def api():
    return {
        "mensagem": "API Sabor & Clic",
        "rotas": {
            "usuarios": "/api/usuarios",
            "pratos": "/api/pratos",
            "pedidos": "/api/pedidos",
            "cozinhas": "/api/cozinhas"
        }
    }


if __name__ == "__main__":
    app.run(debug=True)