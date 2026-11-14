"""Cria as contas locais descritas no README do frontend."""
from app import create_app
from models.usuario import by_email
from services.usuarios import create


def main():
    app = create_app()
    with app.app_context():
        for nome, cargo in (
            ("Administrador Demo", "administrador"),
            ("Cliente Demo", "cliente"),
            ("Cozinheiro Demo", "cozinheiro"),
        ):
            email = f"{cargo}@saborclic.local"
            if by_email(email):
                print(f"Ja existe: {email}")
                continue
            create({
                "nome": nome, "email": email, "senha": "SenhaDemo@2026",
                "cargo": cargo, "turno": "MANHA", "especialidade": "Geral",
            })
            print(f"Criado: {email}")


if __name__ == "__main__":
    main()
