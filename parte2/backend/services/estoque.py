from decimal import Decimal, InvalidOperation
from flask import abort
from database import transaction
from models.base import execute, fetch_one, fetch_all
from services.usuarios import text


def quantity(value, allow_zero=True):
    try:
        number = Decimal(str(value))
        if not number.is_finite() or number < 0 or (not allow_zero and number == 0) or number > Decimal("999999999.999"):
            raise ValueError
        if number.as_tuple().exponent < -3:
            raise ValueError
        return number
    except (InvalidOperation, ValueError):
        abort(400, description="Quantidade invalida (maximo de 3 casas decimais).")


def find(iid, lock=False):
    row = fetch_one("SELECT * FROM Ingrediente WHERE id_ingrediente=%s" + (" FOR UPDATE" if lock else ""), (iid,))
    if not row:
        abort(404, description="Ingrediente nao encontrado.")
    return row


def public(row):
    return {"id": row["id_ingrediente"], "nome": row["nome"], "categoria": row["categoria"] or "",
            "unidade": row["unidade_medida"], "quantidade": float(row["estoque_atual"]),
            "estoque_minimo": float(row["estoque_minimo"]), "validade": row["validade"].isoformat() if row["validade"] else None,
            "custo_unitario": float(row["custo_unitario"])}


def list_all():
    return [public(r) for r in fetch_all("SELECT * FROM Ingrediente ORDER BY nome")]


def create(data):
    values = (text(data, "nome", 60), text(data, "unidade", 20), quantity(data.get("quantidade")),
              quantity(data.get("estoque_minimo")), text(data, "categoria", 50, False))
    with transaction():
        iid, _ = execute("INSERT INTO Ingrediente (nome,unidade_medida,estoque_atual,estoque_minimo,categoria) VALUES (%s,%s,%s,%s,%s)", values)
    return public(find(iid))


def update(iid, data):
    if not isinstance(data, dict) or not data or set(data) - {"nome", "unidade", "categoria", "estoque_minimo", "custo_unitario", "validade", "repor"}:
        abort(400, description="Campos de ingrediente invalidos.")
    fields = []
    values = []
    for key, column, limit in (("nome", "nome", 60), ("unidade", "unidade_medida", 20), ("categoria", "categoria", 50)):
        if key in data:
            fields.append(column + "=%s")
            values.append(text(data, key, limit, key != "categoria"))
    for key in ("estoque_minimo", "custo_unitario"):
        if key in data:
            fields.append(key + "=%s")
            values.append(quantity(data[key]))
    if "validade" in data:
        from datetime import date
        try:
            value = date.fromisoformat(data["validade"]) if data["validade"] else None
        except (ValueError, TypeError):
            abort(400, description="Validade invalida.")
        fields.append("validade=%s")
        values.append(value)
    if "repor" in data:
        fields.append("estoque_atual=estoque_atual+%s")
        values.append(quantity(data["repor"], False))
    with transaction():
        find(iid, True)
        execute("UPDATE Ingrediente SET " + ", ".join(fields) + " WHERE id_ingrediente=%s", tuple(values + [iid]))
    return public(find(iid))


def substitutions(iid):
    find(iid)
    return [{"ingrediente_id": r["id_ingrediente_substituto"], "prioridade": r["nivel_prioridade"]}
            for r in fetch_all("SELECT * FROM Substituicao_Ingrediente WHERE id_ingrediente_principal=%s ORDER BY nivel_prioridade", (iid,))]


def add_substitution(iid, data):
    find(iid)
    sid = data.get("ingrediente_id")
    priority = data.get("prioridade")
    if type(sid) is not int or type(priority) is not int or priority < 1 or sid == iid:
        abort(400, description="Substituicao invalida.")
    find(sid)
    with transaction():
        execute("INSERT INTO Substituicao_Ingrediente (id_ingrediente_principal,id_ingrediente_substituto,nivel_prioridade) VALUES (%s,%s,%s)", (iid, sid, priority))
    return {"ingrediente_id": sid, "prioridade": priority}
