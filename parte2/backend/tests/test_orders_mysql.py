import os
import unittest
from decimal import Decimal
from app import create_app
from database import transaction
from models.base import execute, fetch_one


@unittest.skipUnless(os.getenv("RUN_MYSQL_INTEGRATION") == "1", "MySQL real opcional")
class OrderTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()
        self.pid = None

    def login(self, email):
        token = self.client.get("/api/auth/me").json["csrf"]
        response = self.client.post("/api/auth/login", json={"email": email, "senha": "SenhaDemo@2026"},
                                    headers={"X-CSRF-Token": token})
        self.assertEqual(200, response.status_code)
        return {"X-CSRF-Token": response.json["csrf"]}

    def test_stock_create_order_cancel_and_permissions(self):
        admin = self.login("administrador@saborclic.local")
        with self.app.app_context():
            before = fetch_one("SELECT estoque_atual FROM Ingrediente WHERE id_ingrediente=1")["estoque_atual"]
        token = self.client.get("/api/auth/me").json["csrf"]
        response = self.client.post("/api/ingredientes", json={"nome": "Temporario", "unidade": "kg",
            "quantidade": 2, "estoque_minimo": 1, "categoria": "Teste"}, headers=admin)
        self.assertEqual(201, response.status_code)
        iid = response.json["id"]
        try:
            response = self.client.patch(f"/api/ingredientes/{iid}", json={"repor": 0.5}, headers=admin)
            self.assertEqual(200, response.status_code)
            self.assertEqual(2.5, response.json["quantidade"])
            self.client.post("/api/auth/logout", headers=admin)
            client_headers = self.login("cliente@saborclic.local")
            response = self.client.post("/api/pedidos", json={"itens": [{"prato_id": 1, "quantidade": 2}],
                "endereco_entrega": "Rua Teste"}, headers=client_headers)
            self.assertEqual(201, response.status_code, response.json)
            self.pid = response.json["id"]
            self.assertEqual(56.0, response.json["total"])
            with self.app.app_context():
                reduced = fetch_one("SELECT estoque_atual FROM Ingrediente WHERE id_ingrediente=1")["estoque_atual"]
            self.assertEqual(before - Decimal('0.4'), reduced)
            self.assertEqual(403, self.client.patch(f"/api/pedidos/{self.pid}/status",
                json={"status": "cancelado"}, headers=client_headers).status_code)
            self.client.post("/api/auth/logout", headers=client_headers)
            admin = self.login("administrador@saborclic.local")
            response = self.client.patch(f"/api/pedidos/{self.pid}/status",
                json={"status": "cancelado"}, headers=admin)
            self.assertEqual(200, response.status_code)
            with self.app.app_context():
                restored = fetch_one("SELECT estoque_atual FROM Ingrediente WHERE id_ingrediente=1")["estoque_atual"]
            self.assertEqual(before, restored)
        finally:
            with self.app.app_context():
                with transaction():
                    if self.pid:
                        sale = fetch_one("SELECT id_venda FROM Pedido WHERE id_pedido=%s", (self.pid,))
                        execute("DELETE FROM Pedido_Consumo WHERE id_pedido=%s", (self.pid,))
                        execute("DELETE FROM Item_Pedido WHERE id_pedido=%s", (self.pid,))
                        execute("DELETE FROM Pedido WHERE id_pedido=%s", (self.pid,))
                        if sale and sale['id_venda']:
                            execute("DELETE FROM Venda WHERE id_venda=%s", (sale['id_venda'],))
                    execute("DELETE FROM Ingrediente WHERE id_ingrediente=%s", (iid,))
