import os
import unittest
from datetime import datetime, timedelta
from app import create_app
from database import transaction
from models.base import execute, fetch_all, fetch_one


@unittest.skipUnless(os.getenv('RUN_MYSQL_INTEGRATION') == '1', 'MySQL real opcional')
class OperationsTests(unittest.TestCase):
    def test_reservation_payment_conflict_permissions_and_reports(self):
        app=create_app({'TESTING':True})
        admin=app.test_client()
        client=app.test_client()

        def login(browser,email):
            token=browser.get('/api/auth/me').json['csrf']
            response=browser.post('/api/auth/login',json={'email':email,'senha':'SenhaDemo@2026'},headers={'X-CSRF-Token':token})
            self.assertEqual(200,response.status_code)
            return {'X-CSRF-Token':response.json['csrf']}

        ah=login(admin,'administrador@saborclic.local')
        ch=login(client,'cliente@saborclic.local')
        response=admin.post('/api/bancadas',json={'nome':'Teste temporario','tipo':'Teste','capacidade':2},headers=ah)
        self.assertEqual(201,response.status_code)
        bid=response.json['id']
        try:
            with app.app_context(),transaction():
                execute('UPDATE Bancada SET valor_hora=25 WHERE id_bancada=%s',(bid,))
            start=datetime.now()+timedelta(days=2)
            data={'bancada_id':bid,'inicio':start.isoformat(),'fim':(start+timedelta(hours=2)).isoformat()}
            response=client.post('/api/agendamentos',json=data,headers=ch)
            self.assertEqual(201,response.status_code,response.json)
            aid=response.json['id']
            self.assertEqual(409,client.post('/api/agendamentos',json=data,headers=ch).status_code)
            self.assertEqual(403,client.get('/api/pagamentos').status_code)
            with app.app_context():
                sale=fetch_one('SELECT * FROM Venda WHERE id_agendamento=%s',(aid,))
            self.assertEqual(50,float(sale['valor_pagamento']))
            path=f"/api/pagamentos/{sale['id_venda']}/confirmar"
            self.assertEqual(400,admin.patch(path,json={'forma_pagamento':None},headers=ah).status_code)
            self.assertEqual(200,admin.patch(path,json={'forma_pagamento':'PIX'},headers=ah).status_code)
            self.assertEqual(409,admin.patch(path,json={'forma_pagamento':'PIX'},headers=ah).status_code)
            self.assertEqual(200,client.patch(f'/api/agendamentos/{aid}/cancelar',json={},headers=ch).status_code)
            with app.app_context():
                self.assertEqual('estornado',fetch_one('SELECT status_pagamento FROM Venda WHERE id_agendamento=%s',(aid,))['status_pagamento'])
            response=admin.get('/api/relatorios')
            self.assertEqual(200,response.status_code,response.json)
            self.assertIn('mais_vendidos',response.json)
            self.assertEqual(403,client.get('/api/relatorios').status_code)
        finally:
            with app.app_context(),transaction():
                rows=fetch_all('SELECT id_agendamento FROM Agendamento_Bancada WHERE id_bancada=%s',(bid,))
                for row in rows:
                    execute('DELETE FROM Venda WHERE id_agendamento=%s',(row['id_agendamento'],))
                    execute('DELETE FROM Agendamento_Bancada WHERE id_agendamento=%s',(row['id_agendamento'],))
                    execute('DELETE FROM Agendamento WHERE id_agendamento=%s',(row['id_agendamento'],))
                execute('DELETE FROM Bancada WHERE id_bancada=%s',(bid,))
