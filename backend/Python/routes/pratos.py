from flask import Blueprint, request, jsonify

pratos_bp = Blueprint("pratos", __name__)

pratos = [
    {
        "id": 1,
        "nome": "Hambúrguer Artesanal",
        "preco": 25.90,
        "descricao": "Hambúrguer artesanal com queijo e molho especial"
    },
    {
        "id": 2,
        "nome": "Pizza Calabresa",
        "preco": 39.90,
        "descricao": "Pizza de calabresa com queijo e cebola"
    }
]


# GET /api/pratos
@pratos_bp.route("/", methods=["GET"])
def listar_pratos():
    return jsonify(pratos)


# GET /api/pratos/1
@pratos_bp.route("/<int:id>", methods=["GET"])
def buscar_prato(id):

    prato = next(
        (p for p in pratos if p["id"] == id),
        None
    )

    if prato is None:
        return jsonify({
            "erro": "Prato não encontrado"
        }), 404

    return jsonify(prato)


# POST /api/pratos
@pratos_bp.route("/", methods=["POST"])
def cadastrar_prato():

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Nenhum dado enviado"
        }), 400

    nome = dados.get("nome")
    preco = dados.get("preco")
    descricao = dados.get("descricao")

    if not nome:
        return jsonify({
            "erro": "O nome do prato é obrigatório"
        }), 400

    if preco is None:
        return jsonify({
            "erro": "O preço do prato é obrigatório"
        }), 400

    novo_prato = {
        "id": len(pratos) + 1,
        "nome": nome,
        "preco": float(preco),
        "descricao": descricao or ""
    }

    pratos.append(novo_prato)

    return jsonify(novo_prato), 201


# PUT /api/pratos/1
@pratos_bp.route("/<int:id>", methods=["PUT"])
def atualizar_prato(id):

    prato = next(
        (p for p in pratos if p["id"] == id),
        None
    )

    if prato is None:
        return jsonify({
            "erro": "Prato não encontrado"
        }), 404

    dados = request.get_json()

    if "nome" in dados:
        prato["nome"] = dados["nome"]

    if "preco" in dados:
        prato["preco"] = float(dados["preco"])

    if "descricao" in dados:
        prato["descricao"] = dados["descricao"]

    return jsonify(prato)


# DELETE /api/pratos/1
@pratos_bp.route("/<int:id>", methods=["DELETE"])
def excluir_prato(id):

    prato = next(
        (p for p in pratos if p["id"] == id),
        None
    )

    if prato is None:
        return jsonify({
            "erro": "Prato não encontrado"
        }), 404

    pratos.remove(prato)

    return jsonify({
        "mensagem": "Prato excluído com sucesso"
    })