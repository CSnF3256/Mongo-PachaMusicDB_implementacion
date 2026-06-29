from datetime import datetime
from functools import wraps

from bson import ObjectId
from django.contrib import messages
from django.shortcuts import redirect, render

from .auth import authenticate
from .mongo import ensure_indexes, get_config, get_db, ping


# ─────────────────────────────────────────────────────────────
# Utilidades generales
# ─────────────────────────────────────────────────────────────
def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("usuario"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


def perfil_requerido(*perfiles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            usuario = request.session.get("usuario")
            if not usuario:
                return redirect("login")
            if usuario.get("perfil") not in perfiles:
                messages.error(request, "No tiene permisos para realizar esta acción.")
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def oid(value):
    try:
        return ObjectId(value)
    except Exception:
        return None


def normalize_id(doc):
    if not doc:
        return doc
    doc["id_str"] = str(doc.get("_id"))
    return doc


def normalize_many(docs):
    return [normalize_id(d) for d in docs]


def to_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def mongo_error(request, error):
    messages.error(request, f"Error de MongoDB: {error}")


# ─────────────────────────────────────────────────────────────
# Autenticación local, sin SQL Server
# ─────────────────────────────────────────────────────────────
def login_view(request):
    if request.session.get("usuario"):
        return redirect("dashboard")
    if request.method == "POST":
        user = authenticate(request.POST.get("username"), request.POST.get("password"))
        if user:
            request.session["usuario"] = user
            messages.success(request, f"Bienvenida/o, {user['nombre']}.")
            return redirect("dashboard")
        messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, "login.html")


def logout_view(request):
    request.session.flush()
    return redirect("login")


# ─────────────────────────────────────────────────────────────
# Dashboard MongoDB
# ─────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    cfg = get_config()
    context = {"mongo_uri": cfg.get("mongodb_uri"), "mongo_db": cfg.get("mongodb_database")}
    try:
        ping()
        ensure_indexes()
        db = get_db()
        context.update({
            "conexion_ok": True,
            "total_usuarios": db.usuarios.count_documents({}),
            "total_artistas": db.artistas.count_documents({}),
            "total_albumes": db.albumes.count_documents({}),
            "total_canciones": db.canciones.count_documents({}),
            "total_playlists": db.playlists.count_documents({}),
            "total_ventas": db.ventas.count_documents({}),
            "top_canciones": list(db.canciones.find({}, {"titulo_cancion": 1, "reproducciones_totales": 1, "likes_totales": 1, "generos": 1}).sort("reproducciones_totales", -1).limit(8)),
            "usuarios_premium": list(db.usuarios.find({"tipo_usuario": "Premium"}, {"nombre_usuario": 1, "email_usuario": 1, "pais_usuario": 1}).limit(6)),
            "dist_tipos": [{"label": x.get("_id") or "Sin tipo", "total": x.get("total", 0)} for x in db.usuarios.aggregate([{"$group": {"_id": "$tipo_usuario", "total": {"$sum": 1}}}, {"$sort": {"total": -1}}])],
            "dist_estados": [{"label": x.get("_id") or "Sin estado", "total": x.get("total", 0)} for x in db.canciones.aggregate([{"$group": {"_id": "$estado_cancion", "total": {"$sum": 1}}}, {"$sort": {"total": -1}}])],
        })
    except Exception as e:
        context.update({"conexion_ok": False, "error": str(e)})
    return render(request, "dashboard.html", context)


@login_required
def estado_conexion(request):
    cfg = get_config()
    info = {"config": cfg, "ok": False, "collections": [], "indexes": {}}
    try:
        ping()
        ensure_indexes()
        db = get_db()
        info["ok"] = True
        info["collections"] = sorted(db.list_collection_names())
        for name in ["usuarios", "artistas", "albumes", "canciones", "playlists", "pagos", "reproducciones"]:
            if name in info["collections"]:
                info["indexes"][name] = list(db[name].list_indexes())
    except Exception as e:
        info["error"] = str(e)
    return render(request, "estado_conexion.html", info)


# ─────────────────────────────────────────────────────────────
# CRUD Usuarios
# ─────────────────────────────────────────────────────────────
@login_required
def usuarios_lista(request):
    db = get_db()
    filtro = {}
    q = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    pais = request.GET.get("pais", "").strip()
    if q:
        filtro["$or"] = [
            {"nombre_usuario": {"$regex": q, "$options": "i"}},
            {"email_usuario": {"$regex": q, "$options": "i"}},
        ]
    if tipo:
        filtro["tipo_usuario"] = tipo
    if pais:
        filtro["pais_usuario"] = {"$regex": pais, "$options": "i"}
    docs = normalize_many(list(db.usuarios.find(filtro).sort("nombre_usuario", 1).limit(300)))
    return render(request, "usuarios.html", {
        "usuarios": docs, "q": q, "tipo": tipo, "pais": pais,
        "tipos": sorted([x for x in db.usuarios.distinct("tipo_usuario") if x]),
        "total": len(docs),
    })


@login_required
@perfil_requerido("admin", "editor")
def usuario_form(request, id=None):
    db = get_db()
    doc = normalize_id(db.usuarios.find_one({"_id": oid(id)})) if id else None
    if id and not doc:
        messages.error(request, "Usuario no encontrado.")
        return redirect("usuarios")
    if request.method == "POST":
        data = {
            "nombre_usuario": request.POST.get("nombre_usuario", "").strip(),
            "email_usuario": request.POST.get("email_usuario", "").strip(),
            "pais_usuario": request.POST.get("pais_usuario", "").strip(),
            "tipo_usuario": request.POST.get("tipo_usuario", "Free"),
            "estado_usuario": request.POST.get("estado_usuario", "Activo"),
        }
        if not data["nombre_usuario"] or not data["email_usuario"]:
            messages.error(request, "Nombre y email son obligatorios.")
        else:
            try:
                if doc:
                    db.usuarios.update_one({"_id": doc["_id"]}, {"$set": data})
                    messages.success(request, "Usuario actualizado correctamente en MongoDB.")
                else:
                    data["created_at"] = datetime.utcnow()
                    db.usuarios.insert_one(data)
                    messages.success(request, "Usuario creado correctamente en MongoDB.")
                return redirect("usuarios")
            except Exception as e:
                mongo_error(request, e)
    return render(request, "usuario_form.html", {"item": doc, "accion": "Editar" if doc else "Crear"})


@login_required
@perfil_requerido("admin", "editor")
def usuario_eliminar(request, id):
    if request.method == "POST":
        try:
            get_db().usuarios.delete_one({"_id": oid(id)})
            messages.success(request, "Usuario eliminado de MongoDB.")
        except Exception as e:
            mongo_error(request, e)
    return redirect("usuarios")


# ─────────────────────────────────────────────────────────────
# CRUD Artistas
# ─────────────────────────────────────────────────────────────
@login_required
def artistas_lista(request):
    db = get_db()
    filtro = {}
    q = request.GET.get("q", "").strip()
    pais = request.GET.get("pais", "").strip()
    if q:
        filtro["nombre_artista"] = {"$regex": q, "$options": "i"}
    if pais:
        filtro["pais_artista"] = {"$regex": pais, "$options": "i"}
    docs = normalize_many(list(db.artistas.find(filtro).sort("nombre_artista", 1).limit(300)))
    return render(request, "artistas.html", {"artistas": docs, "q": q, "pais": pais, "total": len(docs)})


@login_required
@perfil_requerido("admin", "editor")
def artista_form(request, id=None):
    db = get_db()
    doc = normalize_id(db.artistas.find_one({"_id": oid(id)})) if id else None
    if id and not doc:
        messages.error(request, "Artista no encontrado.")
        return redirect("artistas")
    if request.method == "POST":
        data = {
            "nombre_artista": request.POST.get("nombre_artista", "").strip(),
            "pais_artista": request.POST.get("pais_artista", "").strip(),
            "descripcion_artista": request.POST.get("descripcion_artista", "").strip(),
            "estado": request.POST.get("estado", "Activo"),
            "discografica": {"nombre_discografica": request.POST.get("discografica", "").strip()},
        }
        if not data["nombre_artista"]:
            messages.error(request, "El nombre del artista es obligatorio.")
        else:
            try:
                if doc:
                    db.artistas.update_one({"_id": doc["_id"]}, {"$set": data})
                    messages.success(request, "Artista actualizado en MongoDB.")
                else:
                    db.artistas.insert_one(data)
                    messages.success(request, "Artista creado en MongoDB.")
                return redirect("artistas")
            except Exception as e:
                mongo_error(request, e)
    return render(request, "artista_form.html", {"item": doc, "accion": "Editar" if doc else "Crear"})


@login_required
@perfil_requerido("admin", "editor")
def artista_eliminar(request, id):
    if request.method == "POST":
        try:
            get_db().artistas.delete_one({"_id": oid(id)})
            messages.success(request, "Artista eliminado de MongoDB.")
        except Exception as e:
            mongo_error(request, e)
    return redirect("artistas")


# ─────────────────────────────────────────────────────────────
# CRUD Álbumes
# ─────────────────────────────────────────────────────────────
def artistas_select(db):
    return normalize_many(list(db.artistas.find({}, {"nombre_artista": 1, "pais_artista": 1}).sort("nombre_artista", 1).limit(500)))


@login_required
def albumes_lista(request):
    db = get_db()
    filtro = {}
    q = request.GET.get("q", "").strip()
    if q:
        filtro["nombre_album"] = {"$regex": q, "$options": "i"}
    docs = normalize_many(list(db.albumes.find(filtro).sort("nombre_album", 1).limit(300)))
    return render(request, "albumes.html", {"albumes": docs, "q": q, "total": len(docs)})


@login_required
@perfil_requerido("admin", "editor")
def album_form(request, id=None):
    db = get_db()
    doc = normalize_id(db.albumes.find_one({"_id": oid(id)})) if id else None
    if id and not doc:
        messages.error(request, "Álbum no encontrado.")
        return redirect("albumes")
    artistas = artistas_select(db)
    if request.method == "POST":
        artista_oid = oid(request.POST.get("artista_id"))
        artista = db.artistas.find_one({"_id": artista_oid}) if artista_oid else None
        data = {
            "nombre_album": request.POST.get("nombre_album", "").strip(),
            "fecha_lanzamiento": request.POST.get("fecha_lanzamiento", "").strip(),
            "estado_album": request.POST.get("estado_album", "Publicado"),
            "artista": {
                "artista_id": artista_oid,
                "nombre_artista": artista.get("nombre_artista") if artista else request.POST.get("nombre_artista", "").strip(),
            },
        }
        if not data["nombre_album"]:
            messages.error(request, "El nombre del álbum es obligatorio.")
        else:
            try:
                if doc:
                    db.albumes.update_one({"_id": doc["_id"]}, {"$set": data})
                    messages.success(request, "Álbum actualizado en MongoDB.")
                else:
                    db.albumes.insert_one(data)
                    messages.success(request, "Álbum creado en MongoDB.")
                return redirect("albumes")
            except Exception as e:
                mongo_error(request, e)
    return render(request, "album_form.html", {"item": doc, "accion": "Editar" if doc else "Crear", "artistas": artistas})


@login_required
@perfil_requerido("admin", "editor")
def album_eliminar(request, id):
    if request.method == "POST":
        try:
            get_db().albumes.delete_one({"_id": oid(id)})
            messages.success(request, "Álbum eliminado de MongoDB.")
        except Exception as e:
            mongo_error(request, e)
    return redirect("albumes")


# ─────────────────────────────────────────────────────────────
# CRUD Canciones
# ─────────────────────────────────────────────────────────────
def albumes_select(db):
    return normalize_many(list(db.albumes.find({}, {"nombre_album": 1, "artista": 1}).sort("nombre_album", 1).limit(500)))


@login_required
def canciones_lista(request):
    db = get_db()
    filtro = {}
    q = request.GET.get("q", "").strip()
    genero = request.GET.get("genero", "").strip()
    estado = request.GET.get("estado", "").strip()
    if q:
        filtro["titulo_cancion"] = {"$regex": q, "$options": "i"}
    if genero:
        filtro["generos"] = genero
    if estado:
        filtro["estado_cancion"] = estado
    docs = normalize_many(list(db.canciones.find(filtro).sort("titulo_cancion", 1).limit(300)))
    generos = sorted([g for g in db.canciones.distinct("generos") if g])
    return render(request, "canciones.html", {"canciones": docs, "q": q, "genero": genero, "estado": estado, "generos": generos, "total": len(docs)})


@login_required
@perfil_requerido("admin", "editor")
def cancion_form(request, id=None):
    db = get_db()
    doc = normalize_id(db.canciones.find_one({"_id": oid(id)})) if id else None
    if id and not doc:
        messages.error(request, "Canción no encontrada.")
        return redirect("canciones")
    albumes = albumes_select(db)
    if request.method == "POST":
        album_oid = oid(request.POST.get("album_id"))
        album = db.albumes.find_one({"_id": album_oid}) if album_oid else None
        generos = [g.strip() for g in request.POST.get("generos", "").split(",") if g.strip()]
        data = {
            "titulo_cancion": request.POST.get("titulo_cancion", "").strip(),
            "duracion_segundos": to_int(request.POST.get("duracion_segundos"), 0),
            "estado_cancion": request.POST.get("estado_cancion", "Activa"),
            "reproducciones_totales": to_int(request.POST.get("reproducciones_totales"), 0),
            "likes_totales": to_int(request.POST.get("likes_totales"), 0),
            "generos": generos,
        }
        if album:
            data["album"] = {"album_id": album_oid, "nombre_album": album.get("nombre_album")}
            art = album.get("artista") or {}
            data["artista"] = {"artista_id": art.get("artista_id"), "nombre_artista": art.get("nombre_artista")}
        if not data["titulo_cancion"]:
            messages.error(request, "El título de la canción es obligatorio.")
        else:
            try:
                if doc:
                    db.canciones.update_one({"_id": doc["_id"]}, {"$set": data})
                    messages.success(request, "Canción actualizada en MongoDB.")
                else:
                    db.canciones.insert_one(data)
                    messages.success(request, "Canción creada en MongoDB.")
                return redirect("canciones")
            except Exception as e:
                mongo_error(request, e)
    return render(request, "cancion_form.html", {"item": doc, "accion": "Editar" if doc else "Crear", "albumes": albumes})


@login_required
@perfil_requerido("admin", "editor")
def cancion_eliminar(request, id):
    if request.method == "POST":
        try:
            get_db().canciones.delete_one({"_id": oid(id)})
            messages.success(request, "Canción eliminada de MongoDB.")
        except Exception as e:
            mongo_error(request, e)
    return redirect("canciones")


# ─────────────────────────────────────────────────────────────
# Playlists y reportes MongoDB
# ─────────────────────────────────────────────────────────────
@login_required
def playlists_lista(request):
    db = get_db()
    q = request.GET.get("q", "").strip()
    filtro = {"nombre_playlist": {"$regex": q, "$options": "i"}} if q else {}
    docs = normalize_many(list(db.playlists.find(filtro).sort("nombre_playlist", 1).limit(200)))
    return render(request, "playlists.html", {"playlists": docs, "q": q, "total": len(docs)})


@login_required
def reportes(request):
    db = get_db()
    context = {}
    try:
        context["top_canciones"] = list(db.canciones.find({}, {"titulo_cancion": 1, "generos": 1, "reproducciones_totales": 1, "likes_totales": 1}).sort("reproducciones_totales", -1).limit(10))
        context["ventas_estado"] = [{"label": x.get("_id") or "Sin estado", "total": x.get("total", 0), "monto": x.get("monto", 0)} for x in db.ventas.aggregate([{"$group": {"_id": "$estado_venta", "total": {"$sum": 1}, "monto": {"$sum": "$total_venta"}}}, {"$sort": {"total": -1}}])]
        context["canciones_lookup"] = list(db.canciones.aggregate([
            {"$lookup": {"from": "albumes", "localField": "album.album_id", "foreignField": "_id", "as": "album_info"}},
            {"$unwind": {"path": "$album_info", "preserveNullAndEmptyArrays": True}},
            {"$project": {"titulo_cancion": 1, "generos": 1, "album_lookup": "$album_info.nombre_album", "artista": "$artista.nombre_artista"}},
            {"$limit": 10},
        ]))
        context["explain_genero"] = db.canciones.find({"generos": "Pop"}).explain().get("queryPlanner", {}).get("winningPlan", {})
    except Exception as e:
        context["error"] = str(e)
    return render(request, "reportes.html", context)
