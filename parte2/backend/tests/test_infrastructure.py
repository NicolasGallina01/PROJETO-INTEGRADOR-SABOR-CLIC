import unittest
from unittest.mock import MagicMock, patch
import mysql.connector
from app import create_app
from database import get_connection, transaction
from models.base import execute


class InfrastructureTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_health_does_not_require_database(self):
        with patch("database.mysql.connector.connect") as connect:
            response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        connect.assert_not_called()

    def test_readiness_closes_cursor_and_connection(self):
        connection = MagicMock()
        connection.cursor.return_value.fetchone.return_value = {"ok": 1}
        with patch("database.mysql.connector.connect", return_value=connection):
            response = self.client.get("/api/ready")
        self.assertEqual(response.status_code, 200)
        connection.cursor.return_value.close.assert_called_once()
        connection.close.assert_called_once()

    def test_unavailable_database_returns_safe_json(self):
        with patch("database.mysql.connector.connect",
                   side_effect=mysql.connector.Error("secret connection details")):
            response = self.client.get("/api/ready")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("secret", response.get_data(as_text=True))

    def test_not_found_is_json(self):
        response = self.client.get("/api/unknown")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["erro"]["codigo"], 404)

    def test_html_errors_and_method_headers(self):
        response = self.client.get('/pagina-inexistente.html')
        self.assertEqual(404, response.status_code)
        self.assertTrue(response.content_type.startswith('text/html'))
        token = self.client.get('/api/auth/me').json['csrf']
        response = self.client.post('/api/health', headers={'X-CSRF-Token': token})
        self.assertEqual(405, response.status_code)
        self.assertIn('GET', response.headers['Allow'])

    def test_bad_json_unauthenticated_and_unexpected_error(self):
        token = self.client.get('/api/auth/me').json['csrf']
        response = self.client.post('/api/auth/login', json=[], headers={'X-CSRF-Token': token})
        self.assertEqual(400, response.status_code)
        self.assertEqual(401, self.client.get('/api/pedidos').status_code)
        with patch('controllers.health_controller.health', side_effect=RuntimeError('private details')):
            # Flask keeps a reference to the registered view function.
            original = self.app.view_functions['health.health']
            self.app.view_functions['health.health'] = lambda: (_ for _ in ()).throw(RuntimeError('private details'))
            try:
                with self.assertLogs(self.app.logger, level='ERROR'):
                    response = self.client.get('/api/health')
            finally:
                self.app.view_functions['health.health'] = original
        self.assertEqual(500, response.status_code)
        self.assertNotIn('private details', response.get_data(as_text=True))

    def test_success_commits_and_reuses_connection(self):
        connection = MagicMock()
        with patch("database.mysql.connector.connect", return_value=connection) as connect:
            with self.app.app_context():
                with transaction():
                    self.assertIs(get_connection(), get_connection())
                    execute("INSERT INTO example (nome) VALUES (%s)", ("teste",))
                connection.commit.assert_called_once()
                connect.assert_called_once()
        connection.close.assert_called_once()

    def test_failure_rolls_back_without_commit(self):
        connection = MagicMock()
        with patch("database.mysql.connector.connect", return_value=connection):
            with self.app.app_context():
                with self.assertRaises(ValueError):
                    with transaction():
                        raise ValueError("invalid")
                connection.rollback.assert_called_once()
                connection.commit.assert_not_called()

    def test_write_requires_transaction(self):
        with self.app.app_context():
            with self.assertRaises(RuntimeError):
                execute("DELETE FROM example")

    def test_nested_transaction_is_rejected_and_rolled_back(self):
        connection = MagicMock()
        with patch("database.mysql.connector.connect", return_value=connection):
            with self.app.app_context():
                with self.assertRaises(RuntimeError):
                    with transaction():
                        with transaction():
                            pass
                connection.commit.assert_not_called()
                connection.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
