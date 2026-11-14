from contextlib import contextmanager
import click
import mysql.connector
from flask import current_app, g


def get_connection():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=current_app.config["MYSQL_HOST"],
            port=current_app.config["MYSQL_PORT"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
            database=current_app.config["MYSQL_DATABASE"],
            connection_timeout=current_app.config["MYSQL_CONNECT_TIMEOUT"],
            charset="utf8mb4",
            autocommit=False,
        )
    return g.db


@contextmanager
def cursor():
    connection = get_connection()
    db_cursor = connection.cursor(dictionary=True)
    try:
        yield db_cursor
    finally:
        db_cursor.close()


@contextmanager
def transaction():
    if g.get("transaction_active", False):
        raise RuntimeError("Transacoes aninhadas nao sao permitidas.")
    connection = get_connection()
    g.transaction_active = True
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        g.transaction_active = False


def close_connection(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        try:
            connection.rollback()
        finally:
            connection.close()


def init_app(app):
    app.teardown_appcontext(close_connection)

    @app.cli.command("check-db")
    def check_db():
        """Verifica conectividade e versao do MySQL configurado."""
        try:
            with cursor() as db_cursor:
                db_cursor.execute("SELECT VERSION() AS version, DATABASE() AS database_name")
                row = db_cursor.fetchone()
            click.echo(f"MySQL {row['version']} | Banco: {row['database_name']}")
        except mysql.connector.Error as error:
            raise click.ClickException(
                "Falha ao conectar ao MySQL. Confira o servidor e o arquivo .env."
            ) from error
