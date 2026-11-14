from datetime import datetime
from decimal import Decimal
from flask import abort
from database import transaction
from models.base import fetch_all, fetch_one, execute



def benches(user):
    return fetch_all('SELECT id_bancada AS id,nome,tipo,capacidade,ativo AS ativa,valor_hora FROM Bancada' + ('' if user['cargo']=='administrador' else ' WHERE ativo=1'))


def add_bench(user, data):
    try:
        rate=Decimal(str(data.get('valor_hora',0)))
        if not rate.is_finite() or rate<0 or rate>99999999 or rate.as_tuple().exponent < -2: raise ValueError()
    except (ValueError, ArithmeticError): abort(400,description='Valor por hora invalido.')
    if not isinstance(data.get('nome'),str) or not data['nome'].strip() or len(data['nome'])>60 or type(data.get('capacidade')) is not int or data['capacidade']<1:
        abort(400, description='Nome e capacidade validos sao obrigatorios.')
    if not isinstance(data.get('tipo',''),str) or len(data.get('tipo',''))>80:
        abort(400)
    with transaction():
        bid,_=execute('INSERT INTO Bancada(nome,tipo,capacidade,valor_hora) VALUES (%s,%s,%s,%s)',(data['nome'].strip(),data.get('tipo',''),data['capacidade'],rate))
    return {'id':bid},201


def update_bench(user, bid, data):
    if type(data.get('ativa')) is not bool:
        abort(400)
    with transaction():
        if not fetch_one('SELECT id_bancada FROM Bancada WHERE id_bancada=%s FOR UPDATE',(bid,)): abort(404)
        execute('UPDATE Bancada SET ativo=%s WHERE id_bancada=%s',(data['ativa'],bid))
    return {'ok':True}


def reservations(user):
    sql='SELECT a.id_agendamento AS id,a.id_usuario AS cliente_id,u.nome AS cliente_nome,a.status,a.observacao,b.id_bancada AS bancada_id,b.nome AS bancada_nome,ab.data_hora_inicio AS inicio,ab.data_hora_fim AS fim FROM Agendamento a JOIN Usuario u ON u.id_usuario=a.id_usuario JOIN Agendamento_Bancada ab ON ab.id_agendamento=a.id_agendamento JOIN Bancada b ON b.id_bancada=ab.id_bancada'
    rows=fetch_all(sql+(' WHERE a.id_usuario=%s' if user['cargo']!='administrador' else '')+' ORDER BY a.id_agendamento DESC',(user['id_usuario'],) if user['cargo']!='administrador' else ())
    for row in rows:
        for key in ('inicio','fim'): row[key]=row[key].isoformat()
    return rows


def list_reservations(user):
    return reservations(user)


def reserve(user, data):
    try:
        start=datetime.fromisoformat(data['inicio'].replace('Z','+00:00'))
        end=datetime.fromisoformat(data['fim'].replace('Z','+00:00'))
        if start.tzinfo: start=start.astimezone().replace(tzinfo=None)
        if end.tzinfo: end=end.astimezone().replace(tzinfo=None)
        if start<=datetime.now() or end<=start: raise ValueError()
        if not 1800 <= (end-start).total_seconds() <= 43200: raise ValueError()
    except (KeyError,TypeError,ValueError,AttributeError): abort(400,description='Escolha um periodo futuro entre 30 minutos e 12 horas.')
    observation=data.get('observacao','')
    if type(data.get('bancada_id')) is not int or not isinstance(observation,str) or len(observation)>500: abort(400)
    with transaction():
        bench=fetch_one('SELECT * FROM Bancada WHERE id_bancada=%s FOR UPDATE',(data['bancada_id'],))
        if not bench or not bench['ativo']: abort(409,description='Bancada indisponivel.')
        if fetch_one("SELECT ab.id_agendamento FROM Agendamento_Bancada ab JOIN Agendamento a ON a.id_agendamento=ab.id_agendamento WHERE ab.id_bancada=%s AND a.status='confirmado' AND ab.data_hora_inicio<%s AND ab.data_hora_fim>%s FOR UPDATE",(data['bancada_id'],end,start)): abort(409,description='Bancada reservada nesse periodo.')
        aid,_=execute('INSERT INTO Agendamento(id_usuario,observacao) VALUES (%s,%s)',(user['id_usuario'],observation))
        execute('INSERT INTO Agendamento_Bancada(id_bancada,id_agendamento,data_hora_inicio,data_hora_fim) VALUES (%s,%s,%s,%s)',(data['bancada_id'],aid,start,end))
        total=(bench['valor_hora']*Decimal(str((end-start).total_seconds()/3600))).quantize(Decimal('.01'))
        if total>Decimal('99999999.99'): abort(400,description='Valor da reserva excede o limite permitido.')
        execute('INSERT INTO Venda(valor_pagamento,id_agendamento) VALUES (%s,%s)',(total,aid))
    return next(row for row in reservations(user) if row['id']==aid),201


def cancel(user, aid):
    with transaction():
        row=fetch_one('SELECT * FROM Agendamento WHERE id_agendamento=%s FOR UPDATE',(aid,))
        if not row: abort(404)
        if user['cargo']!='administrador' and row['id_usuario']!=user['id_usuario']: abort(403)
        if row['status']!='confirmado': abort(409)
        execute("UPDATE Agendamento SET status='cancelado' WHERE id_agendamento=%s",(aid,))
        execute("UPDATE Venda SET status_pagamento=CASE WHEN status_pagamento='pago' THEN 'estornado' ELSE 'cancelado' END WHERE id_agendamento=%s",(aid,))
    return {'ok':True}


def payments(user):
    return fetch_all('SELECT * FROM Venda ORDER BY id_venda DESC')


def pay(user, vid, data):
    method=data.get('forma_pagamento','')
    if not isinstance(method, str): abort(400)
    method=method.upper()
    if method not in ('DINHEIRO','PIX','DEBITO','CREDITO'): abort(400)
    with transaction():
        row=fetch_one('SELECT * FROM Venda WHERE id_venda=%s FOR UPDATE',(vid,))
        if not row: abort(404)
        if row['status_pagamento']!='pendente': abort(409)
        execute("UPDATE Venda SET status_pagamento='pago',forma_pagamento=%s,data_pagamento=NOW() WHERE id_venda=%s",(method,vid))
    return {'ok':True}


def reports(user):
    summary=fetch_one("SELECT COUNT(*) AS pedidos_mes,COALESCE(SUM(CASE WHEN status<>'cancelado' THEN valor_total ELSE 0 END),0) AS receita_mes FROM Pedido WHERE criado_em>=DATE_FORMAT(NOW(),'%Y-%m-01') AND criado_em<DATE_FORMAT(NOW()+INTERVAL 1 MONTH,'%Y-%m-01')")
    summary['receita_mes']=float(summary['receita_mes'])
    summary['reservas_mes']=fetch_one("SELECT COUNT(DISTINCT a.id_agendamento) AS n FROM Agendamento a JOIN Agendamento_Bancada ab ON ab.id_agendamento=a.id_agendamento WHERE a.status='confirmado' AND ab.data_hora_inicio>=DATE_FORMAT(NOW(),'%Y-%m-01') AND ab.data_hora_inicio<DATE_FORMAT(NOW()+INTERVAL 1 MONTH,'%Y-%m-01')")['n']
    summary['estoque_baixo']=fetch_all('SELECT id_ingrediente AS id,nome,estoque_atual AS quantidade,estoque_minimo,unidade_medida AS unidade FROM Ingrediente WHERE estoque_atual<=estoque_minimo')
    summary['mais_vendidos']=fetch_all("SELECT p.nome,SUM(i.quantidade) AS quantidade FROM Item_Pedido i JOIN Prato p ON p.id_prato=i.id_prato JOIN Pedido o ON o.id_pedido=i.id_pedido WHERE o.status<>'cancelado' GROUP BY p.id_prato,p.nome ORDER BY quantidade DESC LIMIT 5")
    summary['por_status']=fetch_all('SELECT status,COUNT(*) AS quantidade FROM Pedido GROUP BY status')
    return summary
