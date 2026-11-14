import os
import unittest

from app import create_app
from database import cursor, get_connection


@unittest.skipUnless(
    os.getenv("RUN_MYSQL_INTEGRATION") == "1",
    "Defina RUN_MYSQL_INTEGRATION=1 para testar o MySQL real.",
)
class MySqlIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})

    def test_database_has_no_triggers(self):
        with self.app.app_context(), cursor() as db_cursor:
            db_cursor.execute('SELECT COUNT(*) AS n FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE()')
            self.assertEqual(0, db_cursor.fetchone()['n'])

    def test_expected_schema_is_present(self):
        expected = {
            "Administrador", "Agendamento", "Agendamento_Bancada", "Bancada",
            "Cliente", "Cozinheiro", "Ficha_Tecnica", "Ingrediente",
            "Item_Pedido", "Pedido", "Prato", "Substituicao_Ingrediente",
            "Usuario", "Venda", "Pedido_Consumo",
        }
        with self.app.app_context():
            with cursor() as db_cursor:
                db_cursor.execute(
                    "SELECT TABLE_NAME FROM information_schema.TABLES "
                    "WHERE TABLE_SCHEMA = DATABASE()"
                )
                actual = {row["TABLE_NAME"].lower() for row in db_cursor.fetchall()}
        self.assertEqual({name.lower() for name in expected}, actual)

    def test_item_insert_does_not_change_stock_automatically(self):
        with self.app.app_context():
            connection = get_connection()
            try:
                with cursor() as db_cursor:
                    db_cursor.execute(
                        "SELECT f.id_prato, f.id_ingrediente, f.quantidade_ingrediente, "
                        "i.estoque_atual, p.preco_unitario "
                        "FROM Ficha_Tecnica f "
                        "JOIN Ingrediente i ON i.id_ingrediente = f.id_ingrediente "
                        "JOIN Prato p ON p.id_prato = f.id_prato "
                        "ORDER BY f.id_prato, f.id_ingrediente LIMIT 1"
                    )
                    row = db_cursor.fetchone()
                    self.assertIsNotNone(row)
                    db_cursor.execute(
                        "INSERT INTO Usuario (nome, email, senha_hash) VALUES (%s, %s, %s)",
                        ("Teste Integracao", "teste.integracao@saborclic.local", "hash-teste"),
                    )
                    user_id = db_cursor.lastrowid
                    db_cursor.execute("INSERT INTO Cliente (id_usuario) VALUES (%s)", (user_id,))
                    db_cursor.execute(
                        "INSERT INTO Pedido (id_cliente, valor_total) VALUES (%s, %s)",
                        (user_id, row["preco_unitario"]),
                    )
                    order_id = db_cursor.lastrowid
                    db_cursor.execute(
                        "INSERT INTO Item_Pedido "
                        "(id_prato, id_pedido, preco_unitario, quantidade) "
                        "VALUES (%s, %s, %s, %s)",
                        (row["id_prato"], order_id, row["preco_unitario"], 1),
                    )
                    db_cursor.execute(
                        "SELECT estoque_atual FROM Ingrediente WHERE id_ingrediente = %s",
                        (row["id_ingrediente"],),
                    )
                    reduced = db_cursor.fetchone()["estoque_atual"]
                    self.assertEqual(row["estoque_atual"], reduced)
            finally:
                connection.rollback()


if __name__ == "__main__":
    unittest.main()
