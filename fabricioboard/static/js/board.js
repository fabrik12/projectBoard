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

    const columns = ['Por Hacer', 'En Progreso', 'Hecho'];

    columns.forEach(columnName => {
        const columnEl = document.createElement('div');
        columnEl.className = 'kanban-column';
        columnEl.innerHTML = `<h2>${columnName}</h2>`;

        // Filtramos las tareas que pertenecen a esta columna
        const columnTasks = data.tasks.filter(task => task.column === columnName);

        // --- ¡NUEVA LÓGICA AQUÍ! ---
        // Iteramos sobre las tareas de la columna para crear sus tarjetas
        columnTasks.forEach(task => {
            const cardEl = document.createElement('div');
            cardEl.className = 'kanban-card';
            cardEl.setAttribute('data-task-id', task.id); // Guardamos el ID de la tarea

            // Renderizamos las etiquetas (tags)
            let tagsHTML = '<div class="card-tags">';
            task.tags.forEach(tag => {
                tagsHTML += `<span class="tag-pill" style="background-color:${tag.color};">${tag.name}</span>`;
            });
            tagsHTML += '</div>';

            // Renderizamos el usuario asignado (si existe)
            let userHTML = '';
            if (task.assigned_user) {
                // Usamos la inicial del nombre de usuario como un "avatar" simple
                const initial = task.assigned_user.username.charAt(0).toUpperCase();
                userHTML = `<div class="user-avatar" title="${task.assigned_user.username}">${initial}</div>`;
            }

            // Construimos el contenido completo de la tarjeta
            cardEl.innerHTML = `
                ${tagsHTML}
                <p class="card-title">${task.title}</p>
                <div class="card-footer">
                    ${userHTML}
                </div>
            `;

            // Añadimos la tarjeta a la columna
            columnEl.appendChild(cardEl);
        });
        // --- FIN DE LA NUEVA LÓGICA ---

        boardContainer.appendChild(columnEl);
    });
}