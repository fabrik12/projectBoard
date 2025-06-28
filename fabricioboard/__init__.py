# fabricioboard/__init__.py
import os
from flask import Flask, render_template

# --- ¡NUEVA IMPORTACIÓN! ---
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_cors import CORS

from .extensions import limiter

def create_app(test_config=None):
    # crea y configura la app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', # Cambiar por un valor aleatorio en producción
        DATABASE=os.path.join(app.instance_path, 'database.db'),
    )

    if test_config is None:
        # carga la configuración de la instancia, si existe
        app.config.from_pyfile('config.py', silent=True)
    else:
        # carga la configuración de prueba
        app.config.from_mapping(test_config)

    # asegúrate de que la carpeta de instancia exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Se inicializa el limitador, usando la dirección IP del visitante como clave.
    limiter.init_app(app)

    # Esto permite que cualquier origen (*) haga peticiones a las rutas bajo /api/
    # En producción, se puede restringir a un dominio específico del frontend.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Registro de la base de datos
    from . import db
    db.init_app(app)

    # Registro del Blueprint de la API
    from . import api
    app.register_blueprint(api.bp)

    # Registro del Blueprint de Administración
    from . import admin
    app.register_blueprint(admin.bp)

    # --- Nueva Ruta para el Frontend ---
    @app.route('/projects/<project_code>')
    def board_view(project_code):
        """
        Renderiza el tablero Kanban para un proyecto específico.
        """
        # Obtenemos los datos del proyecto para pasarlos a la plantilla
        from .db import get_db
        db = get_db()
        project = db.execute(
            'SELECT * FROM projects WHERE code = ?', (project_code,)
        ).fetchone()

        if project is None:
            from flask import abort
            abort(404)

        return render_template('index.html', project=project)

    return app