# fabricioboard/admin.py

import os
from functools import wraps
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from .db import get_db

# Creamos el Blueprint para las rutas de administración
bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(view):
    """
    Este es nuestro decorador "guardián".
    Verifica si el usuario ha iniciado sesión como admin.
    Si no, lo redirige a la página de login.
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if session.get('admin_logged_in') is None:
            return redirect(url_for('admin.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Muestra el dashboard. Ahora también obtiene la lista de usuarios y etiquetas.
    """
    db = get_db()
    projects = db.execute('SELECT id, name, code FROM projects ORDER BY name ASC').fetchall()
    users = db.execute('SELECT id, username, full_name FROM users ORDER BY username ASC').fetchall()
    tags = db.execute('SELECT id, name, color FROM tags ORDER BY name ASC').fetchall()
    
    return render_template('admin/dashboard.html', projects=projects, users=users, tags=tags)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Maneja el login del administrador."""
    if request.method == 'POST':
        password = request.form['password']
        error = None

        # Comparamos la clave enviada con la variable de entorno
        if password != os.environ.get('ADMIN_SECRET_KEY'):
            error = 'Clave incorrecta.'
        
        if error is None:
            # Si la clave es correcta, guardamos el estado en la sesión
            session.clear()
            session['admin_logged_in'] = True
            # Y lo redirigimos al futuro dashboard
            # return redirect(url_for('admin.dashboard')) # <--- Lo activaremos después
            return redirect(url_for('admin.dashboard'))

        flash(error)

    return render_template('admin/login.html')

@bp.route('/logout')
def logout():
    """Limpia la sesión actual para cerrar sesión."""
    session.clear()
    return redirect(url_for('admin.login'))

@bp.route('/projects/create', methods=['POST'])
@admin_required
def create_project():
    """Procesa la creación de un nuevo proyecto."""
    name = request.form['name']
    code = request.form['code']
    
    if not name or not code:
        flash('El nombre y el código son obligatorios.')
    else:
        db = get_db()
        db.execute(
            'INSERT INTO projects (name, code) VALUES (?, ?)',
            (name, code)
        )
        db.commit()
        flash(f'Proyecto "{name}" creado con éxito.')
        
    return redirect(url_for('admin.dashboard'))

@bp.route('/projects/<int:project_id>/delete', methods=['POST'])
@admin_required
def delete_project(project_id):
    """Procesa la eliminación de un proyecto."""
    db = get_db()
    db.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    db.commit()
    flash('Proyecto eliminado con éxito.')
    
    # Recuerda: gracias a "ON DELETE CASCADE" en nuestro schema,
    # todas las tareas asociadas a este proyecto también se eliminarán automáticamente.
    # ¡Una buena decisión de diseño al principio nos ahorra trabajo ahora!
    
    return redirect(url_for('admin.dashboard'))


# --- ¡NUEVAS RUTAS DE GESTIÓN DE USUARIOS! ---
@bp.route('/users/create', methods=['POST'])
@admin_required
def create_user():
    username = request.form['username']
    full_name = request.form['full_name']
    
    if not username:
        flash('El nombre de usuario es obligatorio.')
    else:
        db = get_db()
        db.execute('INSERT INTO users (username, full_name) VALUES (?, ?)', (username, full_name))
        db.commit()
        flash(f'Usuario "{username}" creado.')
        
    return redirect(url_for('admin.dashboard'))

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    db = get_db()
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    flash('Usuario eliminado.')
    return redirect(url_for('admin.dashboard'))


# --- ¡NUEVAS RUTAS DE GESTIÓN DE ETIQUETAS! ---
@bp.route('/tags/create', methods=['POST'])
@admin_required
def create_tag():
    name = request.form['name']
    color = request.form['color']
    
    if not name:
        flash('El nombre de la etiqueta es obligatorio.')
    else:
        db = get_db()
        db.execute('INSERT INTO tags (name, color) VALUES (?, ?)', (name, color))
        db.commit()
        flash(f'Etiqueta "{name}" creada.')

    return redirect(url_for('admin.dashboard'))

@bp.route('/tags/<int:tag_id>/delete', methods=['POST'])
@admin_required
def delete_tag(tag_id):
    db = get_db()
    db.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
    db.commit()
    flash('Etiqueta eliminada.')
    return redirect(url_for('admin.dashboard'))