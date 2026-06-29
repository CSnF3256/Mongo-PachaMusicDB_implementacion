# PachaMusicDB - Implementación Web MongoDB

Este proyecto es una implementación separada de SQL Server. La aplicación usa Django + PyMongo y se conecta únicamente a MongoDB.

## 1. Requisitos

- Python 3.10 o superior.
- MongoDB Community Server activo o MongoDB Compass conectado a `mongodb://localhost:27017/`.
- Base recomendada: `PachaMusicDB`.

## 2. Configurar conexión

Editar `config.json`:

```json
{
  "mongodb_uri": "mongodb://localhost:27017/",
  "mongodb_database": "PachaMusicDB",
  "mongodb_timeout_ms": 5000
}
```

Para Atlas, reemplazar `mongodb_uri` por la cadena del cluster.

## 3. Crear entorno y ejecutar

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abrir:

```txt
http://127.0.0.1:8000/
```

## 4. Credenciales de prueba

- `admin` / `admin2026`
- `editor` / `editor2026`
- `viewer` / `viewer2026`

## 5. Cargar datos de prueba en MongoDB

Si la base está vacía, abre `scripts/carga_masiva_insertmany_mongodb.js` en MongoDB Playground o ejecútalo en `mongosh`:

```powershell
mongosh scripts/carga_masiva_insertmany_mongodb.js
```

Este script usa `insertMany()` para cargar usuarios, artistas, álbumes, canciones, playlists, ventas, pagos, reproducciones e interacciones.

