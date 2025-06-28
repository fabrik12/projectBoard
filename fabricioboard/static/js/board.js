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


// fabricioboard/static/js/board.js

function renderBoard(data) {
    const boardContainer = document.getElementById('kanban-board');
    boardContainer.innerHTML = '';

    const columns = ['Por Hacer', 'En Progreso', 'Hecho'];

    columns.forEach(columnName => {
        const columnEl = document.createElement('div');
        columnEl.className = 'kanban-column';
        // Añadimos un atributo para identificar la columna fácilmente
        columnEl.setAttribute('data-column-name', columnName);

        const columnTitle = document.createElement('h2');
        columnTitle.textContent = columnName;
        columnEl.appendChild(columnTitle);

        // Creamos un contenedor específico para las tarjetas
        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'cards-container';

        const columnTasks = data.tasks.filter(task => task.column === columnName);

        columnTasks.forEach(task => {
            const cardEl = document.createElement('div');
            cardEl.className = 'kanban-card';
            cardEl.setAttribute('data-task-id', task.id);

            // ... (toda la lógica para el innerHTML de la tarjeta sigue igual)
            let tagsHTML = '<div class="card-tags">';
            task.tags.forEach(tag => {
                tagsHTML += `<span class="tag-pill" style="background-color:${tag.color};">${tag.name}</span>`;
            });
            tagsHTML += '</div>';

            let userHTML = '';
            if (task.assigned_user) {
                const initial = task.assigned_user.username.charAt(0).toUpperCase();
                userHTML = `<div class="user-avatar" title="${task.assigned_user.username}">${initial}</div>`;
            }

            cardEl.innerHTML = `
                <div class="card-header">
                    <span class="delete-task" title="Eliminar tarea">&times;</span>
                </div>
                ${tagsHTML}
                <p class="card-title">${task.title}</p>
                <div class="card-footer">
                    ${userHTML}
                </div>
            `;
            // --- ¡NUEVA LÓGICA DE EVENTOS AQUÍ! ---
            // Añadimos el listener para el botón de eliminar
            const deleteButton = cardEl.querySelector('.delete-task');
            deleteButton.addEventListener('click', (event) => {
                event.stopPropagation(); // Evita que se disparen otros eventos en la tarjeta

                const confirmation = confirm('¿Estás seguro de que quieres eliminar esta tarea?');
                if (confirmation) {
                    deleteTask(task.id);
                }
            });
            // --- Fin de la lógica del innerHTML ---

            cardsContainer.appendChild(cardEl);
        });

        columnEl.appendChild(cardsContainer);
        boardContainer.appendChild(columnEl);

        // --- ¡LA MAGIA DE SORTABLEJS EMPIEZA AQUÍ! ---
        new Sortable(cardsContainer, {
            group: 'kanban', // Permite mover tarjetas entre columnas con el mismo grupo
            animation: 150,  // Animación suave al mover
            ghostClass: 'sortable-ghost', // Clase CSS para el "fantasma" de la tarjeta que se arrastra

            // Esta función se dispara cuando sueltas una tarjeta
            onEnd: function (evt) {
                const taskId = evt.item.getAttribute('data-task-id');
                const newColumnName = evt.to.parentElement.getAttribute('data-column-name');
                const newIndex = evt.newDraggableIndex;

                // Llamamos a nuestra API para persistir el cambio
                updateTaskPosition(taskId, newColumnName, newIndex);
            }
        });
    });
}

// --- NUEVA FUNCIÓN ASÍNCRONA PARA ACTUALIZAR EL BACKEND ---
async function updateTaskPosition(taskId, newColumn, newPosition) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                column: newColumn,
                position: newPosition,
            }),
        });

        if (!response.ok) {
            throw new Error('Falló la actualización de la tarea.');
        }

        console.log(`Tarea ${taskId} movida a ${newColumn}, posición ${newPosition}`);
        // Opcional: podrías recargar todo el tablero o simplemente confiar en que el cambio se guardó

    } catch (error) {
        console.error("Error al actualizar la posición:", error);
        // Aquí podrías implementar una alerta para el usuario
        alert("No se pudo mover la tarea. Por favor, refresca la página.");
    }
}

async function deleteTask(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error('Falló la eliminación de la tarea.');
        }

        // Si la API confirma la eliminación, eliminamos la tarjeta del DOM
        const cardToRemove = document.querySelector(`[data-task-id="${taskId}"]`);
        if (cardToRemove) {
            cardToRemove.remove();
        }

        console.log(`Tarea ${taskId} eliminada.`);

    } catch (error) {
        console.error("Error al eliminar la tarea:", error);
        alert("No se pudo eliminar la tarea.");
    }
}