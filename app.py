# app.py

from flask import Flask

# Inicializamos la aplicación Flask
app = Flask(__name__)

# Definimos una ruta de prueba para la raíz del sitio
@app.route('/')
def index():
    """
    Ruta principal que nos servirá para verificar que el servidor funciona.
    """
    return "¡El servidor de FabricioBoard está funcionando!"

# Este bloque asegura que el servidor se ejecute solo cuando ejecutamos este script directamente
if __name__ == '__main__':
    # app.run() inicia el servidor de desarrollo.
    # debug=True permite ver los errores en el navegador y que el servidor se reinicie automáticamente con los cambios.
    app.run(debug=True)