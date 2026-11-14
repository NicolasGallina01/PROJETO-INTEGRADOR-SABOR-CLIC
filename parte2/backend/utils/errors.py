import mysql.connector
from werkzeug.exceptions import HTTPException
from controllers import errors_controller as controller


def register_error_handlers(app):
    app.register_error_handler(HTTPException, controller.http_error)
    app.register_error_handler(mysql.connector.IntegrityError, controller.integrity_error)
    app.register_error_handler(mysql.connector.Error, controller.database_error)
    app.register_error_handler(Exception, controller.unexpected_error)
