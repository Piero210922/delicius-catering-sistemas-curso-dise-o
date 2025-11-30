from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256 as passlib_hash
from sqlalchemy import text
from sqlalchemy.exc import DataError as SADataError
from datetime import datetime
from datetime import date, timedelta
import os
from jinja2 import FileSystemLoader
import smtplib
from email.message import EmailMessage

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Use absolute paths for template and static folders to avoid TemplateNotFound errors
app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
# Ensure Jinja uses the correct templates directory (absolute path)
app.jinja_loader = FileSystemLoader(TEMPLATES_DIR)
app.secret_key = os.getenv('FLASK_SECRET', 'dev-secret')
CORS(app)

MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "catering_db")

# Días mínimos de anticipación para reservar (puedes cambiarlo)
MIN_DAYS_AHEAD = int(os.getenv('MIN_DAYS_AHEAD', '7'))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column('contraseña', db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    # Ampliamos los roles: cliente, admin, cocinero (se removió 'proveedor')
    rol = db.Column(db.Enum('cliente', 'admin', 'cocinero'), nullable=False, server_default='cliente')
    fecha_registro = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    def to_dict(self):
        return {
            'id_usuario': self.id_usuario,
            'nombre_usuario': self.nombre_usuario,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'rol': self.rol,
            'fecha_registro': str(self.fecha_registro)
        }


class Paquete(db.Model):
    __tablename__ = 'paquetes'
    id_paquete = db.Column(db.Integer, primary_key=True)
    nombre_paquete = db.Column(db.Enum('Básico', 'Estándar', 'Premium'), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    precio_base = db.Column(db.Numeric(10,2), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, server_default=text('1'))

    def to_dict(self):
        return {
            'id_paquete': self.id_paquete,
            'nombre_paquete': self.nombre_paquete,
            'descripcion': self.descripcion,
            'precio_base': float(self.precio_base),
            'activo': bool(self.activo)
        }


class Adicional(db.Model):
    __tablename__ = 'adicionales'
    id_adicional = db.Column(db.Integer, primary_key=True)
    nombre_adicional = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10,2), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, server_default=text('1'))

    def to_dict(self):
        return {
            'id_adicional': self.id_adicional,
            'nombre_adicional': self.nombre_adicional,
            'descripcion': self.descripcion,
            'precio': float(self.precio),
            'activo': bool(self.activo)
        }


class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id_pedido = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    id_paquete = db.Column(db.Integer, db.ForeignKey('paquetes.id_paquete', ondelete='RESTRICT'), nullable=False)
    fecha_evento = db.Column(db.Date, nullable=False)
    cantidad_invitados = db.Column(db.Integer, nullable=False)
    precio_total = db.Column(db.Numeric(10,2), nullable=False)
    # Estados: Pendiente -> Confirmado -> En preparación -> Listo para entrega -> Completado | Cancelado
    estado = db.Column(db.Enum('Pendiente', 'Confirmado', 'En preparación', 'Listo para entrega', 'Completado', 'Cancelado'), nullable=False, server_default='Pendiente')
    fecha_creacion = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    fecha_actualizacion = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def to_dict(self):
        return {
            'id_pedido': self.id_pedido,
            'id_usuario': self.id_usuario,
            'id_paquete': self.id_paquete,
            'fecha_evento': str(self.fecha_evento),
            'cantidad_invitados': self.cantidad_invitados,
            'precio_total': float(self.precio_total),
            'estado': self.estado
        }


class MenuEspecial(db.Model):
    __tablename__ = 'menus_especiales'
    id_menu_especial = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido', ondelete='CASCADE'), nullable=False)
    tipo_menu = db.Column(db.Enum('Vegano', 'Celíaco', 'Alérgico'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)


class PedidoAdicional(db.Model):
    __tablename__ = 'pedido_adicionales'
    id_pedido_adicional = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido', ondelete='CASCADE'), nullable=False)
    id_adicional = db.Column(db.Integer, db.ForeignKey('adicionales.id_adicional', ondelete='CASCADE'), nullable=False)


@app.route('/')
def index():
    # Si el usuario en sesión es admin, redirigir directamente al panel de admin
    user = get_current_user()
    if user:
        if user.rol == 'admin':
            return redirect(url_for('admin_pedidos'))
        if user.rol == 'cocinero':
            return redirect(url_for('cocinero_pedidos'))

    # Estadísticas rápidas para la landing
    try:
        count_paquetes = Paquete.query.filter_by(activo=1).count()
        count_adicionales = Adicional.query.filter_by(activo=1).count()
        count_usuarios = Usuario.query.count()
        count_pedidos = Pedido.query.count()
        destacados = Paquete.query.filter_by(activo=1).order_by(Paquete.id_paquete).limit(3).all()
    except Exception:
        # Si la BD no está disponible, pasar valores por defecto
        count_paquetes = count_adicionales = count_usuarios = count_pedidos = 0
        destacados = []

    return render_template('index.html',
                           count_paquetes=count_paquetes,
                           count_adicionales=count_adicionales,
                           count_usuarios=count_usuarios,
                           count_pedidos=count_pedidos,
                           destacados=destacados)


def get_current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return Usuario.query.get(uid)


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash('Necesitas iniciar sesión', 'danger')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)

    return decorated


@app.context_processor
def inject_user():
    return {'current_user': get_current_user()}


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('nombre_usuario')
    password = request.form.get('contraseña')
    if not username or not password:
        flash('Usuario y contraseña requeridos', 'danger')
        return redirect(url_for('login'))

    user = Usuario.query.filter_by(nombre_usuario=username).first()
    if not user:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('login'))

    # verificar hash (asumimos bcrypt-compatible)
    try:
        valid = passlib_hash.verify(password, user.password)
    except Exception:
        valid = False

    if not valid:
        flash('Credenciales inválidas', 'danger')
        return redirect(url_for('login'))

    session['user_id'] = user.id_usuario
    flash(f'Bienvenido {user.nombre_completo}', 'success')
    # Si es admin, enviarlo al panel de administración inmediatamente
    if user.rol == 'admin':
        return redirect(url_for('admin_pedidos'))
    if user.rol == 'cocinero':
        return redirect(url_for('cocinero_pedidos'))

    # Redirect to the order wizard by default so users pueden empezar un pedido tras iniciar sesión
    next_url = request.args.get('next') or url_for('nuevo_pedido')
    return redirect(next_url)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Sesión cerrada', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    nombre_usuario = request.form.get('nombre_usuario')
    contraseña = request.form.get('contraseña')
    nombre_completo = request.form.get('nombre_completo')
    email = request.form.get('email')

    # validaciones básicas
    if not nombre_usuario or not contraseña or not nombre_completo or not email:
        flash('Todos los campos son requeridos', 'danger')
        return redirect(url_for('register'))

    # No aplicamos truncado aquí — usamos pbkdf2_sha256 que no tiene límite de 72 bytes

    # comprobar unicidad
    if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
        flash('El nombre de usuario ya existe', 'danger')
        return redirect(url_for('register'))
    if Usuario.query.filter_by(email=email).first():
        flash('El email ya está en uso', 'danger')
        return redirect(url_for('register'))

    # hashear contraseña y crear usuario
    try:
        hashed = passlib_hash.hash(contraseña)
        nuevo = Usuario(nombre_usuario=nombre_usuario, password=hashed,
                        nombre_completo=nombre_completo, email=email)
        db.session.add(nuevo)
        db.session.commit()
        session['user_id'] = nuevo.id_usuario
        flash('Registro exitoso. Bienvenido!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear usuario: {e}', 'danger')
        return redirect(url_for('register'))


@app.route('/paquetes')
@login_required
def view_paquetes():
    paquetes = Paquete.query.order_by(Paquete.id_paquete).all()
    return render_template('paquetes.html', paquetes=paquetes)


@app.route('/usuarios')
@login_required
def usuarios():
    user = get_current_user()
    if not user or user.rol != 'admin':
        flash('Acceso denegado: administrador requerido', 'danger')
        return redirect(url_for('index'))
    usuarios = Usuario.query.order_by(Usuario.id_usuario).all()
    return render_template('usuarios.html', usuarios=usuarios)


@app.route('/insumos')
@login_required
def insumos():
    user = get_current_user()
    if not user or user.rol != 'admin':
        flash('Acceso denegado: administrador requerido', 'danger')
        return redirect(url_for('index'))
    try:
        result = db.session.execute(text('SELECT * FROM vista_insumos_semanales'))
        insumos = [dict(row._mapping) if hasattr(row, '_mapping') else dict(row) for row in result]
    except Exception:
        insumos = []
    return render_template('insumos.html', insumos=insumos)


@app.route('/adicionales')
@login_required
def view_adicionales():
    adicionales = Adicional.query.filter_by(activo=1).all()
    return render_template('adicionales.html', adicionales=adicionales)


@app.route('/pedidos')
@login_required
def view_pedidos():
    # Obtener pedidos usando ORM para evitar dependencia de vistas de BD
    user = get_current_user()
    try:
        if user and user.rol == 'admin':
            rows = db.session.query(Pedido, Paquete, Usuario).join(Paquete, Pedido.id_paquete == Paquete.id_paquete).join(Usuario, Pedido.id_usuario == Usuario.id_usuario).order_by(Pedido.fecha_creacion.desc()).all()
        else:
            rows = db.session.query(Pedido, Paquete).join(Paquete, Pedido.id_paquete == Paquete.id_paquete).filter(Pedido.id_usuario == user.id_usuario).order_by(Pedido.fecha_creacion.desc()).all()

        pedidos = []
        for row in rows:
            if len(row) == 3:
                pedido, paquete, usuario = row
            else:
                pedido, paquete = row
                usuario = Usuario.query.get(pedido.id_usuario)

            pedidos.append({
                'id_pedido': pedido.id_pedido,
                'id_usuario': pedido.id_usuario,
                'nombre_usuario': usuario.nombre_completo if usuario else None,
                'id_paquete': paquete.id_paquete if paquete else None,
                'nombre_paquete': paquete.nombre_paquete if paquete else None,
                'fecha_evento': str(pedido.fecha_evento),
                'cantidad_invitados': pedido.cantidad_invitados,
                'precio_total': float(pedido.precio_total),
                'estado': pedido.estado
            })
    except Exception:
        pedidos = []

    return render_template('pedidos.html', pedidos=pedidos)


@app.route('/admin/pedidos')
@login_required
def admin_pedidos():
    user = get_current_user()
    if not user or user.rol != 'admin':
        flash('Acceso denegado: administrador requerido', 'danger')
        return redirect(url_for('index'))

    try:
        rows = db.session.query(Pedido, Paquete, Usuario).join(Paquete, Pedido.id_paquete == Paquete.id_paquete).join(Usuario, Pedido.id_usuario == Usuario.id_usuario).order_by(Pedido.fecha_creacion.desc()).all()
        pedidos = []
        for pedido, paquete, usuario in rows:
            pedidos.append({
                'id_pedido': pedido.id_pedido,
                'id_usuario': pedido.id_usuario,
                'nombre_usuario': usuario.nombre_completo if usuario else None,
                'email': usuario.email if usuario else None,
                'id_paquete': paquete.id_paquete if paquete else None,
                'nombre_paquete': paquete.nombre_paquete if paquete else None,
                'fecha_evento': str(pedido.fecha_evento),
                'cantidad_invitados': pedido.cantidad_invitados,
                'precio_total': float(pedido.precio_total),
                'estado': pedido.estado
            })
    except Exception:
        pedidos = []

    return render_template('admin_pedidos.html', pedidos=pedidos)


@app.route('/admin/pedidos/<int:id_pedido>/invoice')
@login_required
def admin_invoice(id_pedido):
    user = get_current_user()
    if not user or user.rol != 'admin':
        flash('Acceso denegado: administrador requerido', 'danger')
        return redirect(url_for('admin_pedidos'))

    pedido = Pedido.query.get_or_404(id_pedido)
    paquete = Paquete.query.get(pedido.id_paquete)
    usuario = Usuario.query.get(pedido.id_usuario)

    # menus especiales
    menus = MenuEspecial.query.filter_by(id_pedido=pedido.id_pedido).all()
    menus_list = [{'tipo': m.tipo_menu, 'cantidad': m.cantidad} for m in menus]

    # adicionales ligados
    ped_adds = db.session.query(PedidoAdicional, Adicional).join(Adicional, PedidoAdicional.id_adicional == Adicional.id_adicional).filter(PedidoAdicional.id_pedido == pedido.id_pedido).all()
    adicionales = []
    for pa, ad in ped_adds:
        adicionales.append({'id_adicional': ad.id_adicional, 'nombre': ad.nombre_adicional, 'precio': float(ad.precio)})

    return render_template('invoice.html', pedido=pedido, paquete=paquete, usuario=usuario, menus=menus_list, adicionales=adicionales)


def send_email(to_address, subject, body_text):
    """Enviar correo simple usando variables de entorno SMTP. Lanza excepción si no configurado o falla.
    """
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    from_email = os.getenv('FROM_EMAIL', smtp_user)

    if not smtp_host or not smtp_user or not smtp_pass:
        raise RuntimeError('SMTP no configurado: falta SMTP_HOST/SMTP_USER/SMTP_PASS')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_address
    msg.set_content(body_text)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)


@app.route('/admin/pedidos/<int:id_pedido>/send_email', methods=['POST'])
@login_required
def admin_send_email(id_pedido):
    user = get_current_user()
    if not user or user.rol != 'admin':
        flash('Acceso denegado: administrador requerido', 'danger')
        return redirect(url_for('admin_pedidos'))

    pedido = Pedido.query.get_or_404(id_pedido)
    usuario = Usuario.query.get(pedido.id_usuario)
    if not usuario:
        flash('Usuario asociado no encontrado.', 'danger')
        return redirect(url_for('admin_pedidos'))

    subject = f"Información sobre su pedido #{pedido.id_pedido}"
    link = url_for('view_pedido', id_pedido=pedido.id_pedido, _external=True)
    body = (
        f"Hola {usuario.nombre_completo},\n\n"
        f"Le contactamos respecto a su pedido para {pedido.fecha_evento}.\n"
        f"Revise los detalles aquí: {link}\n\n"
        "Nos comunicaremos para coordinar la confirmación.\n\n"
        "Saludos,\nDelicious Catering"
    )

    try:
        send_email(usuario.email, subject, body)
        flash('Correo enviado al cliente.', 'success')
    except Exception as e:
        flash(f'No se pudo enviar correo: {e}', 'warning')

    return redirect(url_for('admin_pedidos'))


@app.route('/admin/pedidos/<int:id_pedido>/confirm', methods=['POST'])
@login_required
def admin_confirm_pedido(id_pedido):
    user = get_current_user()
    if not user or user.rol != 'admin':
        flash('Acceso denegado: administrador requerido', 'danger')
        return redirect(url_for('admin_pedidos'))

    pedido = Pedido.query.get_or_404(id_pedido)
    if pedido.estado == 'Confirmado':
        flash('El pedido ya está confirmado.', 'info')
        return redirect(url_for('admin_pedidos'))

    try:
        pedido.estado = 'Confirmado'
        db.session.commit()
        flash('Pedido marcado como Confirmado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al confirmar pedido: {e}', 'danger')

    return redirect(url_for('admin_pedidos'))


@app.route('/admin/pedidos/<int:id_pedido>/complete', methods=['POST'])
@login_required
def admin_complete_pedido(id_pedido):
    user = get_current_user()
    if not user or user.rol != 'admin':
        flash('Acceso denegado: administrador requerido', 'danger')
        return redirect(url_for('admin_pedidos'))

    pedido = Pedido.query.get_or_404(id_pedido)
    desired = 'Completado'
    try:
        pedido.estado = desired
        db.session.commit()
        flash('Pedido marcado como Completado.', 'success')
    except SADataError as de:
        db.session.rollback()
        flash("Error: la base de datos no permite el estado 'Completado'. Ejecuta el ALTER TABLE para ampliar los valores de enum.", 'danger')
        flash("SQL sugerido: ALTER TABLE pedidos MODIFY COLUMN estado ENUM('Pendiente','Confirmado','En preparación','Listo para entrega','Completado','Cancelado') NOT NULL DEFAULT 'Pendiente';", 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar estado: {e}', 'danger')

    return redirect(url_for('admin_pedidos'))


@app.route('/cocinero/pedidos')
@login_required
def cocinero_pedidos():
    user = get_current_user()
    if not user or user.rol != 'cocinero':
        flash('Acceso denegado: cocinero requerido', 'danger')
        return redirect(url_for('index'))

    # Mostrar pedidos que estén en Confirmado, En preparación o Listo para entrega
    try:
        rows = db.session.query(Pedido, Paquete, Usuario).join(Paquete, Pedido.id_paquete == Paquete.id_paquete).join(Usuario, Pedido.id_usuario == Usuario.id_usuario).filter(Pedido.estado.in_(['Confirmado','En preparación','Listo para entrega'])).order_by(Pedido.fecha_evento.asc()).all()
        pedidos = []
        for pedido, paquete, usuario in rows:
            pedidos.append({
                'id_pedido': pedido.id_pedido,
                'id_usuario': pedido.id_usuario,
                'nombre_usuario': usuario.nombre_completo if usuario else None,
                'email': usuario.email if usuario else None,
                'id_paquete': paquete.id_paquete if paquete else None,
                'nombre_paquete': paquete.nombre_paquete if paquete else None,
                'fecha_evento': str(pedido.fecha_evento),
                'cantidad_invitados': pedido.cantidad_invitados,
                'precio_total': float(pedido.precio_total),
                'estado': pedido.estado
            })
    except Exception:
        pedidos = []

    return render_template('cocinero_pedidos.html', pedidos=pedidos)


@app.route('/cocinero/pedidos/<int:id_pedido>/preparacion', methods=['POST'])
@login_required
def cocinero_marcar_preparacion(id_pedido):
    user = get_current_user()
    if not user or user.rol != 'cocinero':
        flash('Acceso denegado: cocinero requerido', 'danger')
        return redirect(url_for('index'))

    pedido = Pedido.query.get_or_404(id_pedido)
    if pedido.estado != 'Confirmado':
        flash('Solo se puede marcar en preparación si está Confirmado.', 'info')
        return redirect(url_for('cocinero_pedidos'))

    # Verify DB accepts this enum value to avoid DataError
    desired = 'En preparación'
    # Intentar actualizar; si falla por DataError (enum), mostrar SQL sugerido
    try:
        pedido.estado = desired
        db.session.commit()
        flash('Pedido marcado como En preparación.', 'success')
    except SADataError as de:
        db.session.rollback()
        flash("Error: la base de datos no permite el estado 'En preparación'. Ejecuta el ALTER TABLE para ampliar los valores de enum (ver mensajes).", 'danger')
        flash("SQL sugerido: ALTER TABLE pedidos MODIFY COLUMN estado ENUM('Pendiente','Confirmado','En preparación','Listo para entrega','Completado','Cancelado') NOT NULL DEFAULT 'Pendiente';", 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar estado: {e}', 'danger')

    return redirect(url_for('cocinero_pedidos'))


@app.route('/cocinero/pedidos/<int:id_pedido>/listo', methods=['POST'])
@login_required
def cocinero_marcar_listo(id_pedido):
    user = get_current_user()
    if not user or user.rol != 'cocinero':
        flash('Acceso denegado: cocinero requerido', 'danger')
        return redirect(url_for('index'))

    pedido = Pedido.query.get_or_404(id_pedido)
    if pedido.estado != 'En preparación':
        flash('Solo se puede marcar Listo para entrega si está En preparación.', 'info')
        return redirect(url_for('cocinero_pedidos'))

    desired = 'Listo para entrega'
    try:
        pedido.estado = desired
        db.session.commit()
        flash('Pedido marcado como Listo para entrega.', 'success')
    except SADataError as de:
        db.session.rollback()
        flash("Error: la base de datos no permite el estado 'Listo para entrega'. Ejecuta el ALTER TABLE para ampliar los valores de enum (ver mensajes).", 'danger')
        flash("SQL sugerido: ALTER TABLE pedidos MODIFY COLUMN estado ENUM('Pendiente','Confirmado','En preparación','Listo para entrega','Completado','Cancelado') NOT NULL DEFAULT 'Pendiente';", 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar estado: {e}', 'danger')

    return redirect(url_for('cocinero_pedidos'))


@app.route('/admin/pedidos/<int:id_pedido>/reject', methods=['POST'])
@login_required
def admin_reject_pedido(id_pedido):
    user = get_current_user()
    if not user or user.rol != 'admin':
        flash('Acceso denegado: administrador requerido', 'danger')
        return redirect(url_for('admin_pedidos'))

    pedido = Pedido.query.get_or_404(id_pedido)
    if pedido.estado != 'Pendiente':
        flash('Solo se pueden rechazar pedidos en estado Pendiente.', 'info')
        return redirect(url_for('admin_pedidos'))

    try:
        pedido.estado = 'Cancelado'
        db.session.commit()
        flash('Pedido rechazado y marcado como Cancelado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al rechazar pedido: {e}', 'danger')

    return redirect(url_for('admin_pedidos'))


@app.route('/pedidos/<int:id_pedido>/cancel', methods=['POST'])
@login_required
def cancel_pedido(id_pedido):
    user = get_current_user()
    pedido = Pedido.query.get_or_404(id_pedido)
    # Only owner or admin can cancel
    if not user or (user.rol != 'admin' and pedido.id_usuario != user.id_usuario):
        flash('No tienes permisos para cancelar este pedido.', 'danger')
        return redirect(url_for('view_pedidos'))

    # No permitir cancelar si ya está confirmado
    if pedido.estado == 'Confirmado':
        flash('No se puede cancelar un pedido que ya fue confirmado.', 'danger')
        return redirect(url_for('view_pedidos'))

    if pedido.estado == 'Cancelado':
        flash('El pedido ya está cancelado.', 'info')
        return redirect(url_for('view_pedidos'))

    try:
        pedido.estado = 'Cancelado'
        db.session.commit()
        flash('Pedido cancelado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cancelar el pedido: {e}', 'danger')

    return redirect(url_for('view_pedidos'))


@app.route('/pedidos/<int:id_pedido>')
@login_required
def view_pedido(id_pedido):
    user = get_current_user()
    pedido = Pedido.query.get_or_404(id_pedido)
    # permission check
    # Allow admin, the order owner, or any cocinero to view details
    if not user or (user.rol != 'admin' and user.rol != 'cocinero' and pedido.id_usuario != user.id_usuario):
        flash('No tienes permisos para ver este pedido.', 'danger')
        return redirect(url_for('view_pedidos'))

    paquete = Paquete.query.get(pedido.id_paquete)
    usuario = Usuario.query.get(pedido.id_usuario)

    # menus especiales
    menus = MenuEspecial.query.filter_by(id_pedido=pedido.id_pedido).all()
    menus_list = [{'tipo': m.tipo_menu, 'cantidad': m.cantidad} for m in menus]

    # adicionales ligados
    ped_adds = db.session.query(PedidoAdicional, Adicional).join(Adicional, PedidoAdicional.id_adicional == Adicional.id_adicional).filter(PedidoAdicional.id_pedido == pedido.id_pedido).all()
    adicionales = []
    for pa, ad in ped_adds:
        adicionales.append({'id_adicional': ad.id_adicional, 'nombre': ad.nombre_adicional, 'precio': float(ad.precio)})

    return render_template('pedido_detalle.html', pedido=pedido, paquete=paquete, usuario=usuario, menus=menus_list, adicionales=adicionales)


def _db_enum_allows(column_schema, table_name, column_name, value):
    """Check INFORMATION_SCHEMA to see if the enum column allows a given value."""
    try:
        sql = "SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s"
        res = db.session.execute(text(sql), (column_schema, table_name, column_name)).fetchone()
        if not res:
            return False
        column_type = res[0]
        # column_type looks like: "enum('Pendiente','Confirmado',...)"
        return f"'{value}'" in column_type
    except Exception:
        return False


@app.route('/pedidos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_pedido():
    if request.method == 'GET':
        usuarios = Usuario.query.all()
        paquetes = Paquete.query.filter_by(activo=1).all()
        adicionales = Adicional.query.filter_by(activo=1).all()
        # Fecha mínima permitida en el input (hoy + MIN_DAYS_AHEAD)
        min_date = (date.today() + timedelta(days=MIN_DAYS_AHEAD)).isoformat()
        return render_template('nuevo_pedido.html', usuarios=usuarios, paquetes=paquetes, adicionales=adicionales, min_date=min_date, min_days=MIN_DAYS_AHEAD)

    # POST: crear pedido
    data = request.form
    try:
        # Preferir id_usuario desde el formulario, si no viene usar el usuario en sesión
        id_usuario = data.get('id_usuario')
        if not id_usuario:
            id_usuario = session.get('user_id')
        id_usuario = int(id_usuario)
        # Validaciones básicas: paquete y fecha son obligatorios
        if not data.get('id_paquete') or not data.get('fecha_evento'):
            flash('Debe seleccionar un paquete y la fecha del evento.', 'danger')
            return redirect(url_for('nuevo_pedido'))

        id_paquete = int(data.get('id_paquete'))
        fecha_evento = data.get('fecha_evento')
        # validar formato de fecha (YYYY-MM-DD)
        try:
            fecha_dt = datetime.strptime(fecha_evento, '%Y-%m-%d').date()
        except Exception:
            flash('Formato de fecha inválido. Use AAAA-MM-DD.', 'danger')
            return redirect(url_for('nuevo_pedido'))

        # Validar anticipación mínima
        earliest = date.today() + timedelta(days=MIN_DAYS_AHEAD)
        if fecha_dt < earliest:
            flash(f'La fecha del evento debe ser al menos {MIN_DAYS_AHEAD} días a partir de hoy ({earliest}).', 'danger')
            return redirect(url_for('nuevo_pedido'))
        cantidad_invitados = int(data.get('cantidad_invitados'))
        adicionales_ids = request.form.getlist('adicionales')

        paquete = Paquete.query.get_or_404(id_paquete)
        precio_base = float(paquete.precio_base)
        # validar invitados mínimos
        if cantidad_invitados < 5:
            flash('La cantidad de invitados debe ser al menos 5.', 'danger')
            return redirect(url_for('nuevo_pedido'))
        precio_total = precio_base * cantidad_invitados

        # Validación: la suma de menús especiales (incluye 'Normal') debe ser igual a la cantidad de invitados
        total_menus = 0
        for tipo in ['Normal', 'Vegano', 'Celíaco', 'Alérgico']:
            key1 = f'menu_{tipo}'
            key2 = f'menu_{tipo.lower()}'
            val = data.get(key1) or data.get(key2)
            try:
                if val:
                    total_menus += int(val)
            except ValueError:
                pass

        if total_menus != cantidad_invitados:
            flash('La suma de menús (incluido Normal) debe ser igual al número de invitados.', 'danger')
            return redirect(url_for('nuevo_pedido'))

        # sumar adicionales: tratarlos como tarifas fijas (una sola suma por adicional)
        for aid in adicionales_ids:
            ad = Adicional.query.get(int(aid))
            if ad:
                precio_total += float(ad.precio)

        pedido = Pedido(id_usuario=id_usuario, id_paquete=id_paquete, fecha_evento=fecha_evento,
                        cantidad_invitados=cantidad_invitados, precio_total=precio_total)
        db.session.add(pedido)
        db.session.commit()

        # insertar adicionales ligados al pedido
        for aid in adicionales_ids:
            pa = PedidoAdicional(id_pedido=pedido.id_pedido, id_adicional=int(aid))
            db.session.add(pa)
        db.session.commit()

        # menus especiales (opcional) - aceptar tanto keys con mayúscula como minúscula
        for tipo in ['Vegano', 'Celíaco', 'Alérgico']:
            key1 = f'menu_{tipo}'            # e.g. menu_Vegano
            key2 = f'menu_{tipo.lower()}'    # e.g. menu_vegano
            val = data.get(key1) or data.get(key2)
            if val:
                try:
                    num = int(val)
                    if num > 0:
                        me = MenuEspecial(id_pedido=pedido.id_pedido, tipo_menu=tipo, cantidad=num)
                        db.session.add(me)
                except ValueError:
                    pass
        db.session.commit()

        flash('Pedido creado correctamente', 'success')
        return redirect(url_for('view_pedidos'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creando pedido: {e}', 'danger')
        return redirect(url_for('nuevo_pedido'))


@app.route('/api/paquetes')
def api_paquetes():
    paquetes = Paquete.query.order_by(Paquete.id_paquete).all()
    return jsonify([p.to_dict() for p in paquetes])


@app.route('/api/adicionales')
def api_adicionales():
    adicionales = Adicional.query.filter_by(activo=1).all()
    return jsonify([a.to_dict() for a in adicionales])


@app.route('/api/pedidos')
def api_pedidos():
    # Return pedidos via ORM for API
    rows = db.session.query(Pedido, Paquete).join(Paquete, Pedido.id_paquete == Paquete.id_paquete).order_by(Pedido.fecha_creacion.desc()).all()
    out = []
    for row in rows:
        pedido, paquete = row
        out.append({
            'id_pedido': pedido.id_pedido,
            'id_usuario': pedido.id_usuario,
            'nombre_paquete': paquete.nombre_paquete if paquete else None,
            'fecha_evento': str(pedido.fecha_evento),
            'cantidad_invitados': pedido.cantidad_invitados,
            'precio_total': float(pedido.precio_total),
            'estado': pedido.estado
        })
    return jsonify(out)


if __name__ == '__main__':
    # Registrar blueprint admin si está disponible
    try:
        from admin import admin_bp
        app.register_blueprint(admin_bp)
    except Exception:
        # Si no existe o hay un error, continuar sin el módulo admin
        pass

    app.run(debug=True)
