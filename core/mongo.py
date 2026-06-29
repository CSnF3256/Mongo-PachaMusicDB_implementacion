import json
from pathlib import Path
from django.conf import settings
from pymongo import MongoClient, ASCENDING, DESCENDING

CONFIG_PATH = Path(settings.BASE_DIR) / "config.json"


def get_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_client():
    cfg = get_config()
    return MongoClient(cfg["mongodb_uri"], serverSelectionTimeoutMS=cfg.get("mongodb_timeout_ms", 5000))


def get_db():
    cfg = get_config()
    return get_client()[cfg["mongodb_database"]]


def ping():
    client = get_client()
    client.admin.command("ping")
    return True


def ensure_indexes():
    db = get_db()
    db.usuarios.create_index([("email_usuario", ASCENDING)], unique=False, name="idx_usuarios_email")
    db.usuarios.create_index([("tipo_usuario", ASCENDING), ("pais_usuario", ASCENDING)], name="idx_usuarios_tipo_pais")
    db.artistas.create_index([("nombre_artista", ASCENDING)], name="idx_artistas_nombre")
    db.artistas.create_index([("pais_artista", ASCENDING)], name="idx_artistas_pais")
    db.albumes.create_index([("nombre_album", ASCENDING)], name="idx_albumes_nombre")
    db.albumes.create_index([("artista.artista_id", ASCENDING)], name="idx_albumes_artista")
    db.canciones.create_index([("titulo_cancion", ASCENDING)], name="idx_canciones_titulo")
    db.canciones.create_index([("generos", ASCENDING)], name="idx_canciones_generos")
    db.canciones.create_index([("reproducciones_totales", DESCENDING)], name="idx_canciones_reproducciones")
    db.playlists.create_index([("usuario.usuario_id", ASCENDING)], name="idx_playlists_usuario")
    db.reproducciones.create_index([("usuario_id", ASCENDING), ("fecha_reproduccion", DESCENDING)], name="idx_reproducciones_usuario_fecha")
    db.pagos.create_index([("estado_pago", ASCENDING), ("fecha_pago", DESCENDING)], name="idx_pagos_estado_fecha")
    return True
