from flask import Blueprint, request, jsonify

usuarios_bp = Blueprint("usuarios", __name__)

usuarios = []


@usuarios_bp.route("/", methods=["GET"])
def listar_usuarios():
    return jsonify(usuarios)


@usuarios_bp.route("/<int:id>", methods=["GET"])
def buscar_usuario(id):

    usuario = next(
        (u for u in usuarios if u["id"] == id),
        None
    )

    if usuario is None:
        return jsonify({
            "erro": "Usuário não encontrado"
        }), 404

    return jsonify(usuario)


@usuarios_bp.route("/", methods=["POST"])
def cadastrar_usuario():

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Dados não enviados"
        }), 400

    nome = dados.get("nome")
    email = dados.get("email")

    if not nome or not email:
        return jsonify({
            "erro": "Nome e email são obrigatórios"
        }), 400

    usuario = {
        "id": len(usuarios) + 1,
        "nome": nome,
        "email": email
    }

    usuarios.append(usuario)

    return jsonify(usuario), 201


@usuarios_bp.route("/<int:id>", methods=["DELETE"])
def excluir_usuario(id):

    usuario = next(
        (u for u in usuarios if u["id"] == id),
        None
    )

    if usuario is None:
        return jsonify({
            "erro": "Usuário não encontrado"
        }), 404

    usuarios.remove(usuario)

    return jsonify({
        "mensagem": "Usuário excluído"
    })