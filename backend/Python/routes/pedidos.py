from flask import Blueprint, request, jsonify

pedidos_bp = Blueprint("pedidos", __name__)

pedidos = []


@pedidos_bp.route("/", methods=["GET"])
def listar_pedidos():

    return jsonify(pedidos)


@pedidos_bp.route("/<int:id>", methods=["GET"])
def buscar_pedido(id):

    pedido = next(
        (p for p in pedidos if p["id"] == id),
        None
    )

    if pedido is None:
        return jsonify({
            "erro": "Pedido não encontrado"
        }), 404

    return jsonify(pedido)


@pedidos_bp.route("/", methods=["POST"])
def criar_pedido():

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Dados não enviados"
        }), 400

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens")

    if not usuario_id:
        return jsonify({
            "erro": "usuario_id é obrigatório"
        }), 400

    if not itens:
        return jsonify({
            "erro": "O pedido precisa possuir itens"
        }), 400

    pedido = {
        "id": len(pedidos) + 1,
        "usuario_id": usuario_id,
        "itens": itens,
        "status": "pendente"
    }

    pedidos.append(pedido)

    return jsonify(pedido), 201


@pedidos_bp.route("/<int:id>/status", methods=["PUT"])
def alterar_status(id):

    pedido = next(
        (p for p in pedidos if p["id"] == id),
        None
    )

    if pedido is None:
        return jsonify({
            "erro": "Pedido não encontrado"
        }), 404

    dados = request.get_json()
    novo_status = dados.get("status")

    status_validos = [
        "pendente",
        "preparando",
        "pronto",
        "entregando",
        "entregue",
        "cancelado"
    ]

    if novo_status not in status_validos:
        return jsonify({
            "erro": "Status inválido"
        }), 400

    pedido["status"] = novo_status

    return jsonify(pedido)