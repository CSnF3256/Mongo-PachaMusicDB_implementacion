import hashlib

USERS = {
    "admin":  {"password_hash": hashlib.sha256("admin2026".encode()).hexdigest(),  "nombre": "Administrador PachaMusic", "perfil": "admin"},
    "editor": {"password_hash": hashlib.sha256("editor2026".encode()).hexdigest(), "nombre": "Editor PachaMusic",        "perfil": "editor"},
    "viewer": {"password_hash": hashlib.sha256("viewer2026".encode()).hexdigest(), "nombre": "Consulta PachaMusic",      "perfil": "viewer"},
}


def authenticate(username, password):
    user = USERS.get((username or "").strip().lower())
    if not user:
        return None
    if hashlib.sha256((password or "").encode()).hexdigest() != user["password_hash"]:
        return None
    return {"username": username.strip().lower(), "nombre": user["nombre"], "perfil": user["perfil"]}
