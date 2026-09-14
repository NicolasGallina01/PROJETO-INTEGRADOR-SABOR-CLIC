from flask import Blueprint, request, jsonify

cozinhas_bp = Blueprint("cozinhas", __name__)

cozinhas = []


@cozinhas_bp.route("/", methods=["GET"])
def listar_cozinhas():
    return jsonify(cozinhas)


@cozinhas_bp.route("/", methods=["POST"])
def cadastrar_cozinha():

    dados = request.get_json()

    nome = dados.get("nome")
    endereco = dados.get("endereco")

    if not nome or not endereco:
        return jsonify({
            "erro": "Nome e endereço são obrigatórios"
        }), 400

    cozinha = {
        "id": len(cozinhas) + 1,
        "nome": nome,
        "endereco": endereco,
        "disponivel": True
    }

    cozinhas.append(cozinha)

    return jsonify(cozinha), 201


@cozinhas_bp.route("/<int:id>/disponibilidade", methods=["PUT"])
def alterar_disponibilidade(id):

    cozinha = next(
        (c for c in cozinhas if c["id"] == id),
        None
    )

    if cozinha is None:
        return jsonify({
            "erro": "Cozinha não encontrada"
        }), 404

    cozinha["disponivel"] = not cozinha["disponivel"]

    return jsonify(cozinha)