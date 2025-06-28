# fabricioboard/api.py

from flask import Blueprint, jsonify, abort
from fabricioboard.db import get_db

# Creamos el Blueprint.
# 'api' es el nombre del blueprint.
# url_prefix='/api' añadirá /api a todas las rutas de este archivo.
bp = Blueprint('api', __name__, url_prefix='/api')

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