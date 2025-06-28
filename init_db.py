# init_db.py

import sqlite3

DB_NAME = 'database.db'
connection = sqlite3.connect(DB_NAME)
cursor = connection.cursor()

# Usamos executescript para ejecutar múltiples sentencias SQL a la vez.
# Esto es más eficiente y asegura que todo se ejecute en una sola transacción.
cursor.executescript("""
-- Eliminar tablas si ya existen para asegurar un estado limpio en cada ejecución
DROP TABLE IF EXISTS task_tags;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS projects;

-- Creación de las tablas en orden de dependencia
-- (Las tablas sin llaves foráneas primero)

CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#FFFFFF'
);

-- Las tablas con llaves foráneas se crean después
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    assigned_user_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    column TEXT NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE TABLE task_tags (
    task_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (task_id, tag_id),
    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
);

""")

print("Tablas creadas con éxito.")

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