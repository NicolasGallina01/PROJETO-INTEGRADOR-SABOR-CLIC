import mysql.connector
from flask import current_app, request, render_template_string


def response(code, message):
    if request.path.startswith('/api/'):
        return {'erro': {'codigo': code, 'mensagem': message}}, code
    return render_template_string('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Erro {{ code }}</title><h1>Erro {{ code }}</h1><p>{{ message }}</p><a href="/">Voltar ao inicio</a></html>', code=code, message=message), code


def http_error(error):
    result = current_app.make_response(response(error.code, error.description))
    for key, value in error.get_headers():
        if key.lower() != 'content-type': result.headers[key] = value
    return result


def integrity_error(error):
    current_app.logger.warning('Restricao MySQL: %s', error.errno)
    return response(409, 'A operacao viola uma restricao dos dados.')


def database_error(error):
    current_app.logger.error('Falha MySQL: %s', error.errno)
    return response(503, 'Banco de dados indisponivel.')


def unexpected_error(error):
    current_app.logger.exception('Erro nao tratado')
    return response(500, 'Erro interno do servidor.')
