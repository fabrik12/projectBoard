# fabricioboard/api.py

from flask import Blueprint, jsonify, abort, request
from fabricioboard.db import get_db

from .extensions import limiter

# Creamos el Blueprint.
# 'api' es el nombre del blueprint.
# url_prefix='/api' añadirá /api a todas las rutas de este archivo.
bp = Blueprint('api', __name__, url_prefix='/api')

# --- ¡NUEVO! Aplicamos un límite por defecto a TODAS las rutas de este blueprint ---
bp.limit = limiter.shared_limit("100 per hour; 20 per minute", scope="api")

@bp.route('/projects/<project_code>', methods=['GET'])
def get_project_data(project_code):
    """
    Endpoint para obtener todos los datos de un tablero (proyecto).
    Esta será la llamada principal al cargar la aplicación.
    """
    db = get_db()
    
    # 1. Buscar el proyecto por su código para obtener su ID y nombre
    project = db.execute('SELECT * FROM projects WHERE code = ?', (project_code,)).fetchone()
    
    # Si el proyecto no existe, devolvemos un error 404 (Not Found)
    if project is None:
        abort(404, description=f"Proyecto con código '{project_code}' no encontrado.")
        
    project_id = project['id']
    
    # 2. Obtener todas las tareas de ese proyecto, incluyendo el nombre del usuario asignado
    tasks_rows = db.execute("""
        SELECT t.*, u.username 
        FROM tasks t
        LEFT JOIN users u ON t.assigned_user_id = u.id
        WHERE t.project_id = ?
        ORDER BY t.position
    """, (project_id,)).fetchall()
    
    # 3. Construir la lista de tareas en formato JSON, añadiendo las etiquetas a cada una
    tasks_list = []
    for task_row in tasks_rows:
        task_dict = dict(task_row) # Convertir la fila a un diccionario completo
        
        # Por cada tarea, buscar sus etiquetas asociadas
        tags_rows = db.execute("""
            SELECT tg.id, tg.name, tg.color
            FROM tags tg
            JOIN task_tags tt ON tg.id = tt.tag_id
            WHERE tt.task_id = ?
        """, (task_dict['id'],)).fetchall()
        
        task_dict['tags'] = [dict(tag) for tag in tags_rows]
        
        # Formatear el usuario asignado para que sea un objeto o nulo
        if task_dict['username']:
            task_dict['assigned_user'] = {'id': task_dict['assigned_user_id'], 'username': task_dict['username']}
        else:
            task_dict['assigned_user'] = None
            
        # Eliminar las claves que no queremos en el JSON final de la tarea
        del task_dict['assigned_user_id']
        del task_dict['project_id']
        # También podemos eliminar el username duplicado
        if 'username' in task_dict:
            del task_dict['username']
        
        tasks_list.append(task_dict)
    
    # 4. Devolver la respuesta final en el formato que diseñamos
    # No es necesario llamar a db.close() aquí, la función teardown_appcontext en db.py se encarga automáticamente.
    return jsonify({
        'project': dict(project),
        'tasks': tasks_list
    })

@bp.route('/tasks', methods=['POST'])
@limiter.limit("5 per minute") # Decorador específico para esta ruta
def create_task():
    """
    Endpoint para crear una nueva tarea.
    Espera un JSON con title, project_id, y column.
    """
    # 1. Obtener los datos del request JSON
    data = request.get_json()

    # 2. Validar que los datos necesarios están presentes
    if not data or not all(k in data for k in ('title', 'project_id', 'column')):
        abort(400, description="Faltan datos requeridos: se necesita 'title', 'project_id' y 'column'.")

    title = data['title']
    project_id = data['project_id']
    column = data['column']
    # La descripción es opcional
    description = data.get('description', '') 
    # El usuario asignado también es opcional
    assigned_user_id = data.get('assigned_user_id', None)

    try:
        db = get_db()
        
        # 3. Calcular la nueva posición de la tarea (la ponemos al final de la columna)
        cursor = db.execute(
            'SELECT COUNT(id) as count FROM tasks WHERE project_id = ? AND column = ?',
            (project_id, column)
        )
        position = cursor.fetchone()['count']

        # 4. Insertar la nueva tarea en la base de datos
        cursor = db.execute(
            """
            INSERT INTO tasks (project_id, assigned_user_id, title, description, column, position)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (project_id, assigned_user_id, title, description, column, position)
        )
        
        new_task_id = cursor.lastrowid
        db.commit()

        # 5. Obtener la tarea recién creada para devolverla en la respuesta
        new_task = db.execute(
            'SELECT * FROM tasks WHERE id = ?', (new_task_id,)
        ).fetchone()

        # El código 201 significa "Created" y es la respuesta estándar para un POST exitoso.
        return jsonify(dict(new_task)), 201

    except db.IntegrityError:
        # Esto podría pasar si, por ejemplo, el project_id no existe.
        abort(400, description="Error de integridad, verifique que los IDs de proyecto y usuario son válidos.")

@bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Endpoint para actualizar una tarea existente.
    Acepta un JSON con los campos a modificar.
    """
    data = request.get_json()
    if not data:
        abort(400, description="No se enviaron datos para actualizar.")

    db = get_db()
    
    # Verificamos primero que la tarea exista
    task = db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if task is None:
        abort(404, description=f"La tarea con id {task_id} no fue encontrada.")

    # Construimos la consulta de actualización dinámicamente
    # para modificar solo los campos que se envían en el JSON.
    fields = []
    values = []
    
    # Campos permitidos para ser actualizados
    allowed_fields = ['title', 'description', 'column', 'position', 'assigned_user_id']
    
    for field in allowed_fields:
        if field in data:
            fields.append(f"{field} = ?")
            values.append(data[field])

    if not fields:
        abort(400, description="Ningún campo válido para actualizar fue proporcionado.")

    values.append(task_id) # Añadimos el id de la tarea al final para el WHERE

    query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
    
    try:
        db.execute(query, tuple(values))
        db.commit()
    except db.Error as e:
        abort(500, description=f"Error en la base de datos: {e}")

    # Devolvemos la tarea actualizada
    updated_task = db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    
    return jsonify(dict(updated_task))


@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Endpoint para eliminar una tarea.
    """
    db = get_db()
    # Verificamos que la tarea exista antes de intentar borrarla
    task = db.execute('SELECT id FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if task is None:
        abort(404, description=f"La tarea con id {task_id} no fue encontrada.")

    db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    
    return jsonify({'success': True, 'message': f'Tarea {task_id} eliminada correctamente.'})


@bp.route('/tasks/<int:task_id>/tags', methods=['POST'])
def assign_tag_to_task(task_id):
    """
    Asigna una etiqueta existente a una tarea existente.
    Espera un JSON con: {"tag_id": <id>}
    """
    data = request.get_json()
    if not data or 'tag_id' not in data:
        abort(400, description="Falta 'tag_id' en el cuerpo del request.")
    
    tag_id = data['tag_id']
    db = get_db()
    
    try:
        db.execute(
            'INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)',
            (task_id, tag_id)
        )
        db.commit()
    except db.IntegrityError:
        # Esto puede pasar si la tarea o el tag no existen, o si la asignación ya existe.
        abort(400, description="Error de integridad: la tarea/etiqueta no existe o la asignación ya fue hecha.")
        
    return jsonify({'success': True, 'message': f'Etiqueta {tag_id} asignada a la tarea {task_id}.'}), 201

@bp.route('/tasks/<int:task_id>/tags/<int:tag_id>', methods=['DELETE'])
def unassign_tag_from_task(task_id, tag_id):
    """
    Desasigna una etiqueta de una tarea.
    """
    db = get_db()
    # La sentencia DELETE no da error si la fila no existe, pero es buena práctica verificar.
    result = db.execute(
        'DELETE FROM task_tags WHERE task_id = ? AND tag_id = ?',
        (task_id, tag_id)
    )
    db.commit()

    if result.rowcount == 0:
        # Si no se borró ninguna fila, es porque la asignación no existía.
        abort(404, description="La asignación especificada no fue encontrada.")

    return jsonify({'success': True, 'message': f'Etiqueta {tag_id} desasignada de la tarea {task_id}.'})