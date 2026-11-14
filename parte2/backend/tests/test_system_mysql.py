import os
import secrets
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from app import create_app
from database import transaction
from models.base import execute, fetch_all, fetch_one


@unittest.skipUnless(os.getenv('RUN_MYSQL_INTEGRATION') == '1', 'MySQL real opcional')
class SystemTests(unittest.TestCase):
    def setUp(self):
        self.app=create_app({'TESTING':True})
        self.admin,self.ah=self.login('administrador@saborclic.local')
        self.client,self.ch=self.login('cliente@saborclic.local')
        self.cook,self.kh=self.login('cozinheiro@saborclic.local')
        self.iid=self.pid=self.bid=None

    def login(self,email):
        browser=self.app.test_client()
        token=browser.get('/api/auth/me').json['csrf']
        r=browser.post('/api/auth/login',json={'email':email,'senha':'SenhaDemo@2026'},headers={'X-CSRF-Token':token})
        self.assertEqual(200,r.status_code)
        return browser,{'X-CSRF-Token':r.json['csrf']}

    def tearDown(self):
        with self.app.app_context(),transaction():
            if self.pid:
                orders=fetch_all('SELECT DISTINCT p.id_pedido,p.id_venda FROM Pedido p JOIN Item_Pedido i ON i.id_pedido=p.id_pedido WHERE i.id_prato=%s',(self.pid,))
                for order in orders:
                    for table in ('Pedido_Consumo','Item_Pedido','Pedido'):
                        execute(f'DELETE FROM {table} WHERE id_pedido=%s',(order['id_pedido'],))
                    execute('DELETE FROM Venda WHERE id_venda=%s',(order['id_venda'],))
                execute('DELETE FROM Ficha_Tecnica WHERE id_prato=%s',(self.pid,))
                execute('DELETE FROM Prato WHERE id_prato=%s',(self.pid,))
            if self.iid: execute('DELETE FROM Ingrediente WHERE id_ingrediente=%s',(self.iid,))
            if self.bid:
                for row in fetch_all('SELECT id_agendamento FROM Agendamento_Bancada WHERE id_bancada=%s',(self.bid,)):
                    for table in ('Venda','Agendamento_Bancada','Agendamento'):
                        execute(f'DELETE FROM {table} WHERE id_agendamento=%s',(row['id_agendamento'],))
                execute('DELETE FROM Bancada WHERE id_bancada=%s',(self.bid,))

    def test_catalog_checkout_kitchen_delivery_and_payment(self):
        r=self.admin.post('/api/ingredientes',json={'nome':'QA ingrediente','unidade':'un','categoria':'QA','quantidade':2,'estoque_minimo':1},headers=self.ah)
        self.assertEqual(201,r.status_code,r.json)
        self.iid=r.json['id']
        dish={'nome':'QA '+secrets.token_hex(4),'categoria':'QA','preco':10,'tempo_preparo':15,'ativo':False}
        r=self.admin.post('/api/pratos',json=dish,headers=self.ah)
        self.assertEqual(201,r.status_code,r.json)
        self.pid=r.json['id']
        path=f'/api/pratos/{self.pid}'
        dish['ativo']=True
        self.assertEqual(409,self.admin.put(path,json=dish,headers=self.ah).status_code)
        self.assertEqual(400,self.admin.put(path+'/ficha',json={'ingredientes':[{'ingrediente_id':self.iid,'quantidade':0.0001}]},headers=self.ah).status_code)
        self.assertEqual(200,self.admin.put(path+'/ficha',json={'ingredientes':[{'ingrediente_id':self.iid,'quantidade':1}]},headers=self.ah).status_code)
        self.assertEqual(200,self.admin.put(path,json=dish,headers=self.ah).status_code)
        payload={'itens':[{'prato_id':self.pid,'quantidade':3}],'forma_pagamento':'cartao'}
        self.assertEqual(409,self.client.post('/api/pedidos',json=payload,headers=self.ch).status_code)
        payload['itens'][0]['quantidade']=2
        r=self.client.post('/api/pedidos',json=payload,headers=self.ch)
        self.assertEqual(201,r.status_code,r.json)
        oid=r.json['id']
        self.assertEqual(20,r.json['total'])
        self.assertEqual(409,self.client.post('/api/pedidos',json=payload,headers=self.ch).status_code)
        for status in ('em_preparo','pronto'):
            self.assertEqual(200,self.cook.patch(f'/api/pedidos/{oid}/status',json={'status':status},headers=self.kh).status_code)
        self.assertEqual(403,self.cook.patch(f'/api/pedidos/{oid}/status',json={'status':'entregue'},headers=self.kh).status_code)
        self.assertEqual(200,self.admin.patch(f'/api/pedidos/{oid}/status',json={'status':'entregue'},headers=self.ah).status_code)
        with self.app.app_context():
            vid=fetch_one('SELECT id_venda FROM Pedido WHERE id_pedido=%s',(oid,))['id_venda']
            self.assertEqual(0,fetch_one('SELECT estoque_atual FROM Ingrediente WHERE id_ingrediente=%s',(self.iid,))['estoque_atual'])
        self.assertEqual(200,self.admin.patch(f'/api/pagamentos/{vid}/confirmar',json={'forma_pagamento':'CREDITO'},headers=self.ah).status_code)
        self.assertEqual(200,self.admin.get('/api/relatorios').status_code)

    def test_simultaneous_reservations_and_owner_isolation(self):
        r=self.admin.post('/api/bancadas',json={'nome':'QA concorrencia','tipo':'QA','capacidade':2,'valor_hora':20},headers=self.ah)
        self.assertEqual(201,r.status_code)
        self.bid=r.json['id']
        start=datetime.now()+timedelta(days=3)
        payload={'bancada_id':self.bid,'inicio':start.isoformat(),'fim':(start+timedelta(hours=1)).isoformat()}
        second,headers=self.login('cliente@saborclic.local')
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(browser.post,'/api/agendamentos',json=payload,headers=h) for browser,h in ((self.client,self.ch),(second,headers))]
            responses=[f.result() for f in futures]
        self.assertEqual([201,409],sorted(r.status_code for r in responses))
        self.assertEqual(403,self.cook.get('/api/agendamentos').status_code)
        self.assertEqual(403,self.client.get('/api/relatorios').status_code)
