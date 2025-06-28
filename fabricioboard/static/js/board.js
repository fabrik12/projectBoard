// fabricioboard/static/js/board.js

document.addEventListener('DOMContentLoaded', () => {
    // Esta función se ejecuta cuando el HTML ha sido completamente cargado.
    if (typeof PROJECT_CODE !== 'undefined') {
        fetchAndRenderBoard(PROJECT_CODE);
    }
});

async function fetchAndRenderBoard(projectCode) {
    try {
        // 1. Llamamos a nuestra propia API que ya construimos
        const response = await fetch(`/api/projects/${projectCode}`);
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        const data = await response.json();

        // 2. Renderizamos el tablero con los datos recibidos
        renderBoard(data);

    } catch (error) {
        console.error('No se pudo cargar el tablero:', error);
        document.getElementById('kanban-board').innerHTML = '<p>Error al cargar el tablero. Verifique el código del proyecto.</p>';
    }
}

function renderBoard(data) {
    const boardContainer = document.getElementById('kanban-board');
    boardContainer.innerHTML = ''; // Limpiamos el contenedor

    // Definimos las columnas que queremos renderizar (podríamos obtenerlas de la data a futuro)
    const columns = ['Por Hacer', 'En Progreso', 'Hecho'];

    columns.forEach(columnName => {
        // Creamos el elemento de la columna
        const columnEl = document.createElement('div');
        columnEl.className = 'kanban-column';
        columnEl.innerHTML = `<h2>${columnName}</h2>`;

        // Filtramos las tareas que pertenecen a esta columna
        const columnTasks = data.tasks.filter(task => task.column === columnName);

        // (Próximo paso: Renderizar las tarjetas de las tareas aquí)
        // Por ahora, solo añadimos la columna vacía

        boardContainer.appendChild(columnEl);
    });
}