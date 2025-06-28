# projectBoard

## TBoard v1.0

`TBoard` es una aplicación web ligera diseñada para la gestión de proyectos mediante tableros Kanban. Permite a equipos pequeños y grupos de estudio colaborar en tiempo real sin la necesidad de un sistema de login complejo, accediendo a cada tablero a través de un "código de proyecto" único.

## ✨ Características Principales

- Visualización por Proyecto: Accede a un tablero Kanban único y compartido simplemente navegando a la URL con el código del proyecto.

- Gestión de Tareas (CRUD): La interfaz permite crear, editar títulos y eliminar tareas de forma interactiva.

- Arrastrar y Soltar (Drag & Drop): Reordena tareas y cambia su estado (columna) de manera fluida e intuitiva.

- Asignación de Recursos: Asigna usuarios y etiquetas a las tareas a través de un modal de detalles para una mejor organización.

- Filtros Dinámicos: Filtra las tareas visibles en el tablero por usuario o etiqueta con un solo clic para enfocarte en lo que importa.

- Persistencia Ligera: Todos los datos se guardan en una base de datos SQLite.

## 🛠️ Tecnologías Utilizadas

- Backend: Flask

- Base de Datos: SQLite

- Frontend: JavaScript (Vanilla JS, ES6+), HTML5, CSS3

- Librerías Externas: SortableJS

## 🚀 Puesta en Marcha Local

Para ejecutar el proyecto en tu máquina local, sigue estos pasos:

1. Clona el repositorio:

```Bash
git clone <url-del-repositorio>
cd fabricioboard
```

2. Crea y activa un entorno virtual:

```Bash
# Para macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Para Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Instala las dependencias:
   El proyecto incluye dependencias como Flask, Flask-CORS y Gunicorn. Instálalas junto con el paquete del proyecto en modo editable:

```Bash
pip install -e .
```

4. Configura las variables de entorno:

```Bash
# En macOS/Linux
export FLASK_APP=fabricioboard
export FLASK_ENV=development

# En Windows
set FLASK_APP=fabricioboard
set FLASK_ENV=development
```

5. Inicializa la base de datos:
   Este comando creará el archivo database.db con el esquema necesario.

```Bash
flask init-db
```

_(Opcional: puedes ejecutar el script init_db.py para poblar la base de datos con datos de ejemplo)._

6. Ejecuta la aplicación:

```Bash
flask run
```

El servidor estará disponible en http://127.0.0.1:5000.

## 💻 Uso

Para visualizar un tablero, abre tu navegador y navega a:
http://127.0.0.1:5000/projects/CODIGO_DEL_PROYECTO

Reemplaza CODIGO_DEL_PROYECTO con un código de proyecto válido que exista en tu base de datos (ej. FAB-01 si usaste los datos de ejemplo).
