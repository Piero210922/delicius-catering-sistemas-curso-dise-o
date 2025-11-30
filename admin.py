from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.exceptions import abort
import sys
from passlib.hash import pbkdf2_sha256 as passlib_hash

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')


def _get_app_module():
    # Intentar obtener el módulo correcto independientemente de cómo se ejecute (python app.py vs flask run)
    return sys.modules.get('app') or sys.modules.get('__main__')


def require_admin():
    app_mod = _get_app_module()
    get_current_user = getattr(app_mod, 'get_current_user', None)
    if not get_current_user:
        abort(403)
    user = get_current_user()
    if not user or user.rol != 'admin':
        abort(403)


@admin_bp.route('/usuarios')
def usuarios():
    # Requerir login simple
    if not session.get('user_id'):
        flash('Necesitas iniciar sesión', 'danger')
        return redirect(url_for('login'))
    require_admin()
    app_mod = _get_app_module()
    Usuario = getattr(app_mod, 'Usuario')
    users = Usuario.query.order_by(Usuario.id_usuario).all()
    return render_template('admin_usuarios.html', usuarios=users)


@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
def nuevo_usuario():
    if not session.get('user_id'):
        flash('Necesitas iniciar sesión', 'danger')
        return redirect(url_for('login'))
    require_admin()
    app_mod = _get_app_module()
    Usuario = getattr(app_mod, 'Usuario')
    db = getattr(app_mod, 'db')

    if request.method == 'GET':
        return render_template('admin_usuario_form.html', usuario=None)

    nombre_usuario = request.form.get('nombre_usuario')
    contraseña = request.form.get('contraseña')
    nombre_completo = request.form.get('nombre_completo')
    email = request.form.get('email')
    rol = request.form.get('rol') or 'cliente'
    allowed_roles = ['cliente', 'admin', 'cocinero']
    if rol not in allowed_roles:
        flash('Rol inválido seleccionado', 'danger')
        return redirect(url_for('admin_bp.nuevo_usuario'))

    if not nombre_usuario or not contraseña or not nombre_completo or not email:
        flash('Todos los campos marcados son obligatorios', 'danger')
        return redirect(url_for('admin_bp.nuevo_usuario'))

    if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
        flash('El nombre de usuario ya existe', 'danger')
        return redirect(url_for('admin_bp.nuevo_usuario'))
    if Usuario.query.filter_by(email=email).first():
        flash('El email ya está en uso', 'danger')
        return redirect(url_for('admin_bp.nuevo_usuario'))

    try:
        hashed = passlib_hash.hash(contraseña)
        u = Usuario(nombre_usuario=nombre_usuario, password=hashed, nombre_completo=nombre_completo, email=email, rol=rol)
        db.session.add(u)
        db.session.commit()
        flash('Usuario creado correctamente', 'success')
        return redirect(url_for('admin_bp.usuarios'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creando usuario: {e}', 'danger')
        return redirect(url_for('admin_bp.nuevo_usuario'))


@admin_bp.route('/usuarios/<int:id_usuario>/editar', methods=['GET', 'POST'])
def editar_usuario(id_usuario):
    if not session.get('user_id'):
        flash('Necesitas iniciar sesión', 'danger')
        return redirect(url_for('login'))
    require_admin()
    app_mod = _get_app_module()
    Usuario = getattr(app_mod, 'Usuario')
    db = getattr(app_mod, 'db')
    usuario = Usuario.query.get_or_404(id_usuario)
    if request.method == 'GET':
        return render_template('admin_usuario_form.html', usuario=usuario)

    nombre_completo = request.form.get('nombre_completo')
    email = request.form.get('email')
    rol = request.form.get('rol') or usuario.rol
    allowed_roles = ['cliente', 'admin', 'cocinero']
    if rol not in allowed_roles:
        flash('Rol inválido seleccionado', 'danger')
        return redirect(url_for('admin_bp.editar_usuario', id_usuario=id_usuario))
    contraseña = request.form.get('contraseña')

    if not nombre_completo or not email:
        flash('Nombre completo y email son obligatorios', 'danger')
        return redirect(url_for('admin_bp.editar_usuario', id_usuario=id_usuario))

    # comprobar unicidad de email
    existing = Usuario.query.filter(Usuario.email == email, Usuario.id_usuario != id_usuario).first()
    if existing:
        flash('El email ya está en uso por otro usuario', 'danger')
        return redirect(url_for('admin_bp.editar_usuario', id_usuario=id_usuario))

    # Evitar que un admin se quite a sí mismo como admin (bloqueo accidental)
    current_user_id = session.get('user_id')
    if current_user_id and current_user_id == id_usuario and usuario.rol == 'admin' and rol != 'admin':
        flash('No puedes quitarte el rol de administrador a ti mismo.', 'danger')
        return redirect(url_for('admin_bp.editar_usuario', id_usuario=id_usuario))

    try:
        usuario.nombre_completo = nombre_completo
        usuario.email = email
        usuario.rol = rol
        if contraseña:
            usuario.password = passlib_hash.hash(contraseña)
        db.session.commit()
        flash('Usuario actualizado', 'success')
        return redirect(url_for('admin_bp.usuarios'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {e}', 'danger')
        return redirect(url_for('admin_bp.editar_usuario', id_usuario=id_usuario))


@admin_bp.route('/usuarios/<int:id_usuario>/borrar', methods=['POST'])
def borrar_usuario(id_usuario):
    if not session.get('user_id'):
        flash('Necesitas iniciar sesión', 'danger')
        return redirect(url_for('login'))
    require_admin()
    app_mod = _get_app_module()
    Usuario = getattr(app_mod, 'Usuario')
    db = getattr(app_mod, 'db')
    usuario = Usuario.query.get_or_404(id_usuario)
    # Evitar que un admin se borre a sí mismo
    current_user_id = session.get('user_id')
    if current_user_id and current_user_id == id_usuario:
        flash('No puedes eliminar tu propia cuenta desde aquí.', 'danger')
        return redirect(url_for('admin_bp.usuarios'))

    try:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar usuario: {e}', 'danger')
    return redirect(url_for('admin_bp.usuarios'))
