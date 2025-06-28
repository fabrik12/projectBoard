# run.py

from fabricioboard import create_app

# Llamamos a la función de fábrica para obtener una instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Ejecutamos la aplicación en modo de depuración.
    # Para un entorno de producción, se usaría un servidor WSGI como Gunicorn.
    app.run(debug=True, host='0.0.0.0', port=5000)