# init_db.py

import sqlite3

DB_NAME = 'instance/database.db'
connection = sqlite3.connect(DB_NAME)
cursor = connection.cursor()

# --- Inserción de Datos de Ejemplo ---
try:
    # Crear un proyecto de ejemplo
    cursor.execute("INSERT INTO projects (code, name) VALUES (?, ?)", ('FAB-01', 'Mi Primer Proyecto Kanban'))
    project_id = cursor.lastrowid

    # Crear usuarios de ejemplo
    cursor.execute("INSERT INTO users (username, full_name) VALUES (?, ?)", ('fabricio', 'Fabricio Aldunate'))
    user_fabricio_id = cursor.lastrowid
    cursor.execute("INSERT INTO users (username, full_name) VALUES (?, ?)", ('viernes', 'Viernes AI'))
    user_viernes_id = cursor.lastrowid

    # Crear etiquetas de ejemplo
    cursor.execute("INSERT INTO tags (name, color) VALUES (?, ?)", ('bug', '#d73a4a'))
    tag_bug_id = cursor.lastrowid
    cursor.execute("INSERT INTO tags (name, color) VALUES (?, ?)", ('feature', '#0366d6'))
    tag_feature_id = cursor.lastrowid

    # Crear tareas de ejemplo en diferentes columnas
    tasks_to_add = [
        (project_id, user_fabricio_id, 'Configurar el entorno de desarrollo', 'Instalar Python, Flask y crear el repo.', 'Por Hacer', 0),
        (project_id, user_viernes_id, 'Diseñar el esquema de la base de datos', 'Definir tablas, columnas y relaciones.', 'En Progreso', 0),
        (project_id, None, 'Crear la API para tareas', 'Endpoint para GET de todas las tareas.', 'En Progreso', 1),
        (project_id, user_fabricio_id, 'Implementar la vista del tablero', '', 'Hecho', 0),
    ]
    cursor.executemany("""
        INSERT INTO tasks (project_id, assigned_user_id, title, description, column, position)
        VALUES (?, ?, ?, ?, ?, ?)
    """, tasks_to_add)

    # Asignar etiquetas a las tareas
    # A la tarea de 'Diseñar BD' (ID: 2) le asignamos la etiqueta 'feature' (ID: 2)
    cursor.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)", (2, tag_feature_id))
    # A la tarea de 'Crear API' (ID: 3) le asignamos 'feature' también
    cursor.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)", (3, tag_feature_id))
    
    print("Datos de ejemplo insertados correctamente.")

except sqlite3.IntegrityError as e:
    print(f"Error al insertar datos de ejemplo (es posible que ya existan): {e}")


# Guardamos los cambios y cerramos la conexión
connection.commit()
connection.close()

print(f"Base de datos '{DB_NAME}' inicializada y poblada con datos de ejemplo.")