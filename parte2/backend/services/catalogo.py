from decimal import Decimal, InvalidOperation
from flask import abort
from database import transaction
from models.base import fetch_one, fetch_all, execute
from services.usuarios import text


def number(value):
    try:
        result = Decimal(str(value))
        if not result.is_finite() or result <= 0 or result > Decimal("99999999.99") or result.as_tuple().exponent < -2:
            raise ValueError()
        return result
    except (InvalidOperation, ValueError):
        abort(400, description="Informe um preco positivo com ate duas casas decimais.")


def dish(pid, lock=False):
    row = fetch_one("SELECT * FROM Prato WHERE id_prato=%s" + (" FOR UPDATE" if lock else ""), (pid,))
    if not row:
        abort(404, description="Prato nao encontrado.")
    return row


def public(row):
    return {"id": row["id_prato"], "nome": row["nome"], "categoria": row["categoria"],
            "preco": float(row["preco_unitario"]), "desc": row["descricao"] or "",
            "img": row["imagem_url"] or "", "tempo_preparo": row["tempo_preparo"],
            "ativo": bool(row["ativo"])}


def save(data, pid=None):
    values = [text(data, "nome", 100), number(data.get("preco")),
              text(data, "categoria", 50), text(data, "desc", 10000, False),
              text(data, "img", 2048, False)]
    tempo = data.get("tempo_preparo")
    ativo = data.get("ativo", False)
    if isinstance(tempo, bool) or not isinstance(tempo, int) or not 1 <= tempo <= 1440 or not isinstance(ativo, bool):
        abort(400, description="Tempo ou disponibilidade invalidos.")
    if values[4] and not values[4].startswith(("https://", "http://")):
        abort(400, description="URL da imagem invalida.")
    with transaction():
        if pid:
            dish(pid, True)
        if ativo and (not pid or not fetch_one("SELECT id_prato FROM Ficha_Tecnica WHERE id_prato=%s LIMIT 1", (pid,))):
            abort(409, description="Cadastre a ficha tecnica antes de ativar o prato.")
        values += [tempo, ativo]
        if pid:
            execute("UPDATE Prato SET nome=%s,preco_unitario=%s,categoria=%s,descricao=%s,imagem_url=%s,tempo_preparo=%s,ativo=%s WHERE id_prato=%s",
                    tuple(values + [pid]))
        else:
            pid, _ = execute("INSERT INTO Prato (nome,preco_unitario,categoria,descricao,imagem_url,tempo_preparo,ativo) VALUES (%s,%s,%s,%s,%s,%s,%s)", tuple(values))
    return public(dish(pid))


def recipe(pid, rows):
    if not isinstance(rows, list):
        abort(400)
    validated = []
    ids = set()
    for row in rows:
        if not isinstance(row, dict) or type(row.get("ingrediente_id")) is not int:
            abort(400)
        iid = row["ingrediente_id"]
        if iid in ids:
            abort(400, description="Ingrediente repetido.")
        ids.add(iid)
        from services.estoque import quantity
        validated.append((pid, iid, quantity(row.get("quantidade"), False)))
    with transaction():
        prato = dish(pid, True)
        if prato["ativo"] and not rows:
            abort(409, description="Inative o prato antes de esvaziar a ficha.")
        for _, iid, _ in validated:
            if not fetch_one("SELECT id_ingrediente FROM Ingrediente WHERE id_ingrediente=%s", (iid,)):
                abort(400, description="Ingrediente inexistente.")
        execute("DELETE FROM Ficha_Tecnica WHERE id_prato=%s", (pid,))
        for values in validated:
            execute("INSERT INTO Ficha_Tecnica (id_prato,id_ingrediente,quantidade_ingrediente) VALUES (%s,%s,%s)", values)
    return {"ok": True}
