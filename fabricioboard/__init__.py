# fabricioboard/__init__.py
import os
from flask import Flask

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

    # Registro de la base de datos
    from . import db
    db.init_app(app)

    # Registro del Blueprint de la API
    from . import api
    app.register_blueprint(api.bp)

    return app