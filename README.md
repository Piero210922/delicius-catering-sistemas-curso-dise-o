# Proyecto: Sistema de Catering (Flask + MySQL)

Plantilla mínima para un sistema de pedidos de catering: backend en Flask, conexión a MySQL y frontend con plantillas Jinja2.

Requisitos:
- Python 3.8+
- MySQL o MariaDB

Pasos rápidos (PowerShell en Windows):

1) Crear y activar entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependencias

```powershell
pip install -r requirements.txt
```

3) Crear `.env` a partir de `.env.example` y completar credenciales MySQL

4) Si prefieres controlar el esquema con `flask-migrate` (opcional):

```powershell
$env:FLASK_APP = "app.py"
flask db init
flask db migrate -m "initial"
flask db upgrade
```

Si ya tienes la base de datos creada con el SQL proporcionado, no necesitas correr las migraciones.

5) Ejecutar la aplicación

```powershell
python app.py
```

API JSON disponibles:
- `GET /api/paquetes`
- `GET /api/adicionales`
- `GET /api/pedidos`

Notas de buenas prácticas:
- Mantén las credenciales en `.env` y no las subas al repositorio.
- Hashea siempre las contraseñas al crear usuarios (usa `bcrypt` o `argon2`).
- Valida entradas en frontend y backend.
