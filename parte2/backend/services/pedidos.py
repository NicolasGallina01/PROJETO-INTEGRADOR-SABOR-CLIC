from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from flask import abort
from database import cursor, transaction
from models.base import fetch_one, fetch_all, execute
from services.usuarios import text

STATUSES = ("aguardando", "em_preparo", "pronto", "entregue", "cancelado")


def get(pid, lock=False):
    row = fetch_one("SELECT p.*, u.nome AS cliente FROM Pedido p JOIN Usuario u ON u.id_usuario=p.id_cliente WHERE p.id_pedido=%s" + (" FOR UPDATE" if lock else ""), (pid,))
    if not row:
        abort(404, description="Pedido nao encontrado.")
    return row


def public(row):
    items = fetch_all("SELECT i.*, p.nome FROM Item_Pedido i JOIN Prato p ON p.id_prato=i.id_prato WHERE i.id_pedido=%s", (row["id_pedido"],))
    minutes = max(0, round((row["prazo_estimado"] - row["criado_em"]).total_seconds() / 60)) if row["prazo_estimado"] else 0
    return {"id": row["id_pedido"], "cliente_id": row["id_cliente"], "cliente": row["cliente"],
            "cozinheiro_id": row["id_cozinheiro"], "status": row["status"], "total": float(row["valor_total"]),
            "tempo_estimado": minutes, "criado_em": row["criado_em"].isoformat(),
            "endereco_entrega": row["endereco_entrega"] or "",
            "itens": [{"prato_id": i["id_prato"], "nome": i["nome"], "quantidade": i["quantidade"],
                       "preco_unitario": float(i["preco_unitario"])} for i in items]}


def list_for(user):
    if user["cargo"] == "cliente":
        rows = fetch_all("SELECT p.*,u.nome AS cliente FROM Pedido p JOIN Usuario u ON u.id_usuario=p.id_cliente WHERE p.id_cliente=%s ORDER BY p.id_pedido DESC", (user["id_usuario"],))
    else:
        rows = fetch_all("SELECT p.*,u.nome AS cliente FROM Pedido p JOIN Usuario u ON u.id_usuario=p.id_cliente ORDER BY p.id_pedido DESC")
    return [public(row) for row in rows]


def create(user, data):
    raw = data.get("itens")
    if not isinstance(raw, list) or not raw or len(raw) > 50:
        abort(400, description="Informe de 1 a 50 itens.")
    quantities = defaultdict(int)
    for item in raw:
        if not isinstance(item, dict) or type(item.get("prato_id")) is not int or type(item.get("quantidade")) is not int or not 1 <= item["quantidade"] <= 50:
            abort(400, description="Item invalido.")
        quantities[item["prato_id"]] += item["quantidade"]
        if quantities[item["prato_id"]] > 50:
            abort(400, description="Quantidade maxima por prato: 50.")
    address = text(data, "endereco_entrega", 255, False)
    payment = str(data.get('forma_pagamento', 'PIX')).upper()
    payment = {'CARTAO': 'CREDITO', 'CARTÃO': 'CREDITO'}.get(payment, payment)
    if payment not in ('PIX', 'DINHEIRO', 'DEBITO', 'CREDITO'):
        abort(400, description='Forma de pagamento invalida.')
    with transaction():
        # Lock dos pratos e ingredientes sempre em ordem, evitando vendas
        # simultaneas acima do estoque e diminuindo deadlocks.
        dishes = {}
        requirements = defaultdict(Decimal)
        for pid in sorted(quantities):
            row = fetch_one("SELECT * FROM Prato WHERE id_prato=%s FOR UPDATE", (pid,))
            if not row or not row["ativo"]:
                abort(409, description="Um prato nao esta disponivel.")
            recipe = fetch_all("SELECT * FROM Ficha_Tecnica WHERE id_prato=%s", (pid,))
            if not recipe:
                abort(409, description="Prato sem ficha tecnica.")
            dishes[pid] = row
            for ingredient in recipe:
                requirements[ingredient["id_ingrediente"]] += ingredient["quantidade_ingrediente"] * quantities[pid]
        for iid in sorted(requirements):
            row = fetch_one("SELECT estoque_atual,nome FROM Ingrediente WHERE id_ingrediente=%s FOR UPDATE", (iid,))
            if not row or row["estoque_atual"] < requirements[iid]:
                abort(409, description=f"Estoque insuficiente para {row['nome'] if row else 'um ingrediente'}.")
        total = sum((dishes[pid]["preco_unitario"] * count for pid, count in quantities.items()), Decimal(0))
        estimate = max(dishes[pid]["tempo_preparo"] for pid in quantities)
        sale_id, _ = execute('INSERT INTO Venda(valor_pagamento,forma_pagamento) VALUES (%s,%s)', (total,payment))
        order_id, _ = execute(
            "INSERT INTO Pedido (id_cliente,endereco_entrega,prazo_estimado,valor_total) VALUES (%s,%s,%s,%s)",
            (user["id_usuario"], address, datetime.now() + timedelta(minutes=estimate), total))
        execute('UPDATE Pedido SET id_venda=%s WHERE id_pedido=%s', (sale_id,order_id))
        for pid, count in quantities.items():
            execute("INSERT INTO Item_Pedido (id_prato,id_pedido,preco_unitario,quantidade) VALUES (%s,%s,%s,%s)",
                    (pid, order_id, dishes[pid]["preco_unitario"], count))
        for iid, amount in requirements.items():
            execute("INSERT INTO Pedido_Consumo (id_pedido,id_ingrediente,quantidade) VALUES (%s,%s,%s)",
                    (order_id, iid, amount))
            execute("UPDATE Ingrediente SET estoque_atual=estoque_atual-%s WHERE id_ingrediente=%s", (amount, iid))
    return public(get(order_id))


def change_status(user, pid, status):
    if status not in STATUSES:
        abort(400, description="Status invalido.")
    with transaction():
        row = get(pid, True)
        transitions = {"aguardando": {"em_preparo", "cancelado"}, "em_preparo": {"pronto", "cancelado"},
                       "pronto": {"entregue"}, "entregue": set(), "cancelado": set()}
        if status not in transitions[row["status"]]:
            abort(409, description="Mudanca de status invalida.")
        if status == "entregue" and user["cargo"] != "administrador":
            abort(403)
        if status in {"em_preparo", "pronto"} and user["cargo"] == "cozinheiro":
            if row["id_cozinheiro"] and row["id_cozinheiro"] != user["id_usuario"]:
                abort(403, description="Pedido atribuido a outro cozinheiro.")
            if not row["id_cozinheiro"]:
                execute("UPDATE Pedido SET id_cozinheiro=%s WHERE id_pedido=%s", (user["id_usuario"], pid))
        if status == "cancelado":
            execute("UPDATE Venda SET status_pagamento=CASE WHEN status_pagamento='pago' THEN 'estornado' ELSE 'cancelado' END WHERE id_venda=%s", (row['id_venda'],))
            requirements = fetch_all(
                "SELECT id_ingrediente,quantidade AS amount FROM Pedido_Consumo "
                "WHERE id_pedido=%s ORDER BY id_ingrediente", (pid,))
            for item in requirements:
                execute("UPDATE Ingrediente SET estoque_atual=estoque_atual+%s WHERE id_ingrediente=%s",
                        (item["amount"], item["id_ingrediente"]))
        execute("UPDATE Pedido SET status=%s WHERE id_pedido=%s", (status, pid))
    return public(get(pid))


def change_time(user, pid, minutes):
    if type(minutes) is not int or not 1 <= minutes <= 240:
        abort(400, description="Estimativa deve ter entre 1 e 240 minutos.")
    with transaction():
        row = get(pid, True)
        if row["status"] not in {"aguardando", "em_preparo"}:
            abort(409, description="Pedido ja finalizado.")
        if user["cargo"] == "cozinheiro" and row["id_cozinheiro"] and row["id_cozinheiro"] != user["id_usuario"]:
            abort(403)
        execute("UPDATE Pedido SET prazo_estimado=%s WHERE id_pedido=%s",
                (row["criado_em"] + timedelta(minutes=minutes), pid))
    return public(get(pid))
