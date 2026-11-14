from pathlib import Path
from flask import send_from_directory

frontend = Path(__file__).resolve().parents[2] / "frontend"

def index():
    return send_from_directory(frontend / "templates", "login.html")

def page(page):
    return send_from_directory(frontend / "templates", page + ".html")

def script(name):
    return send_from_directory(frontend / "script", name)

def style(name):
    return send_from_directory(frontend / "style", name)

def root_script(name):
    return send_from_directory(frontend / "script", name + ".js")

def root_style():
    return send_from_directory(frontend / "style", "style.css")
