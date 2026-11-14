from services.health_service import check_database


def health():
    return {"status": "online", "sistema": "Sabor & Clic"}


def readiness():
    check_database()
    return {"status": "ready", "database": "mysql"}
