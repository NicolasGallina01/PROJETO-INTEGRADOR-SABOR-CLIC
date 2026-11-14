import os
import secrets
import unittest
from app import create_app
from database import transaction
from models.base import execute
from models import usuario


@unittest.skipUnless(os.getenv("RUN_MYSQL_INTEGRATION") == "1", "MySQL real opcional")
class AuthTests(unittest.TestCase):
    def test_registration_login_permissions_and_logout(self):
        app = create_app({"TESTING": True})
        client = app.test_client()
        email = secrets.token_hex(10) + "@teste.local"
        password = "SenhaTeste!2026"
        uid = None
        try:
            with client.get("/") as response:
                self.assertEqual(200, response.status_code)
            with client.get("/app.js") as response:
                self.assertEqual(200, response.status_code)
            token = client.get("/api/auth/me").json["csrf"]
            headers = {"X-CSRF-Token": token}
            response = client.post("/api/auth/registro", json={
                "nome": "Teste", "email": email, "senha": password, "cargo": "administrador"
            }, headers=headers)
            self.assertEqual(201, response.status_code)
            uid = response.json["usuario"]["id"]
            self.assertEqual("cliente", response.json["usuario"]["cargo"])
            with app.app_context():
                self.assertNotEqual(password, usuario.find(uid)["senha_hash"])
            self.assertEqual(403, client.post("/api/auth/login", json={}).status_code)
            response = client.post("/api/auth/login", json={"email": email, "senha": password}, headers=headers)
            self.assertEqual(200, response.status_code)
            token = response.json["csrf"]
            self.assertEqual(403, client.get("/api/usuarios").status_code)
            self.assertEqual(200, client.get("/api/pratos").status_code)
            self.assertEqual(200, client.post("/api/auth/logout", json={}, headers={"X-CSRF-Token": token}).status_code)
            self.assertEqual(401, client.get("/api/pratos").status_code)
        finally:
            if uid:
                with app.app_context():
                    with transaction():
                        execute("DELETE FROM Cliente WHERE id_usuario=%s", (uid,))
                        execute("DELETE FROM Usuario WHERE id_usuario=%s", (uid,))
