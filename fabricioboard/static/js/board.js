// fabricioboard/static/js/board.js

let currentBoardData = {};
let activeFilters = { userId: null, tagId: null };

document.addEventListener('DOMContentLoaded', () => {
    // Esta función se ejecuta cuando el HTML ha sido completamente cargado.
    if (typeof PROJECT_CODE !== 'undefined') {
        fetchAndRenderBoard(PROJECT_CODE);
    }

    // Añadimos los listeners para cerrar el modal aquí dentro.
    // Esto asegura que los botones #close-modal-btn y #modal-backdrop
    // existen en el DOM antes de intentar asignarles un evento de clic.
    document.getElementById('close-modal-btn').addEventListener('click', closeModal);
    document.getElementById('modal-backdrop').addEventListener('click', closeModal);
});

async function fetchAndRenderBoard(projectCode) {
    try {
        // 1. Llamamos a nuestra propia API que ya construimos
        const response = await fetch(`/api/projects/${projectCode}`);
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        const data = await response.json();

        currentBoardData = data;

        //Renderizamos el tablero con los datos recibidos
        renderBoard(data);
        renderFilters(currentBoardData);

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

            // --- ¡NUEVA LÓGICA PARA EDICIÓN DE TÍTULO! ---
            const titleElement = cardEl.querySelector('.card-title');
            titleElement.addEventListener('click', () => {
                // Obtenemos el título actual y el ID de la tarea
                const currentTitle = titleElement.textContent;
                const taskId = cardEl.getAttribute('data-task-id');

                // Creamos el campo de input
                const inputEl = document.createElement('input');
                inputEl.type = 'text';
                inputEl.className = 'card-title-input';
                inputEl.value = currentTitle;

                // Reemplazamos el título por el input
                titleElement.style.display = 'none';
                titleElement.parentElement.insertBefore(inputEl, titleElement.nextSibling);
                inputEl.focus();

                // Función para guardar los cambios
                const saveChanges = async () => {
                    const newTitle = inputEl.value.trim();
                    // Solo guardamos si el título es válido y ha cambiado
                    if (newTitle && newTitle !== currentTitle) {
                        titleElement.textContent = newTitle; // Actualización optimista de la UI
                        await updateTask(taskId, { title: newTitle });
                    }
                    // Restauramos la vista
                    inputEl.remove();
                    titleElement.style.display = 'block';
                };

                // Guardar al presionar "Enter"
                inputEl.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        inputEl.blur(); // El evento 'blur' se encargará de guardar
                    }
                });

                // Guardar cuando el input pierde el foco (clic fuera)
                inputEl.addEventListener('blur', saveChanges);
            });

            cardEl.addEventListener('click', (event) => {
                // Solo abre el modal si no se hizo clic en un elemento interactivo
                if (!event.target.closest('.delete-task, .card-title')) {
                    openTaskModal(task.id);
                }
            });

            // --- Fin de la lógica del innerHTML ---

            cardsContainer.appendChild(cardEl);
        });

        columnEl.appendChild(cardsContainer);
        // --- ¡NUEVA LÓGICA PARA EL BOTÓN DE AÑADIR! ---
        const addCardButton = document.createElement('button');
        addCardButton.className = 'add-card-btn';
        addCardButton.textContent = '+ Añadir una tarjeta...';

        addCardButton.addEventListener('click', () => {
            // Ocultamos el botón y mostramos el formulario de creación
            addCardButton.style.display = 'none';
            const form = createCardForm(columnName, addCardButton);
            columnEl.appendChild(form);
            form.querySelector('textarea').focus();
        });

        columnEl.appendChild(addCardButton)

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
                updateTask(taskId, { column: newColumnName, position: newIndex })
            }
        });
    });
}

// --- BLOQUE DE FUNCIONES DE API ---

async function updateTask(taskId, dataToUpdate) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dataToUpdate),
        });

        if (!response.ok) throw new Error('Falló la actualización de la tarea.');

        console.log(`Tarea ${taskId} actualizada con:`, dataToUpdate);
    } catch (error) {
        console.error("Error al actualizar la tarea:", error);
        alert("No se pudo actualizar la tarea.");
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


// --- FIN FUNCIONES API ---

function createCardForm(columnName, addButton) {
    const form = document.createElement('div');
    form.className = 'create-card-form';

    const textarea = document.createElement('textarea');
    textarea.placeholder = 'Introduce un título para esta tarjeta...';

    const saveButton = document.createElement('button');
    saveButton.textContent = 'Guardar Tarjeta';

    const cancelButton = document.createElement('button');
    cancelButton.className = 'cancel-btn';
    cancelButton.textContent = '×';

    // Evento para guardar
    saveButton.addEventListener('click', () => {
        const title = textarea.value.trim();
        if (title) {
            // Llamamos a la nueva función que se conecta con la API
            createTask(title, columnName, PROJECT_CODE);
        }
    });

    // Evento para cancelar (cierra el form y muestra el botón de nuevo)
    cancelButton.addEventListener('click', () => {
        form.remove();
        addButton.style.display = 'block';
    });

    form.appendChild(textarea);
    form.appendChild(saveButton);
    form.appendChild(cancelButton);

    return form;
}

async function createTask(title, column, projectCode) {
    // Extraemos el ID del proyecto desde el JSON inicial
    // (Esto es una simplificación, en una app más grande lo manejaríamos diferente)
    const response_data = await fetch(`/api/projects/${projectCode}`);
    const data = await response_data.json();
    const projectId = data.project.id;

    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                project_id: projectId,
                column: column,
            }),
        });

        if (!response.ok) {
            throw new Error('Falló la creación de la tarea.');
        }

        // Si la creación es exitosa, simplemente recargamos todo el tablero
        // Es la forma más sencilla de asegurar que todo está sincronizado.
        fetchAndRenderBoard(projectCode);

    } catch (error) {
        console.error("Error al crear la tarea:", error);
        alert("No se pudo crear la tarea.");
    }
}


// --- PARA MODAL ---
function openTaskModal(taskId) {
    const task = currentBoardData.tasks.find(t => t.id === taskId);
    if (!task) return;

    // Poblar datos básicos
    document.getElementById('modal-task-title').textContent = task.title;
    document.getElementById('modal-task-description').textContent = task.description || 'No hay descripción.';

    // Poblar y manejar usuarios
    const usersList = document.getElementById('modal-users-list');
    usersList.innerHTML = '';
    // Necesitamos la lista completa de usuarios del proyecto. Asumimos que la API la proveerá.
    // Por ahora, usemos los usuarios que ya tenemos en las tareas.
    const allUsers = [...new Set(currentBoardData.tasks.map(t => t.assigned_user).filter(Boolean).map(u => u.username))];
    allUsers.forEach(username => {
        const user = currentBoardData.tasks.find(t => t.assigned_user && t.assigned_user.username === username).assigned_user;
        const userEl = document.createElement('div');
        userEl.className = 'list-item';
        userEl.textContent = user.username;
        if (task.assigned_user && task.assigned_user.id === user.id) {
            userEl.classList.add('selected');
        }
        userEl.addEventListener('click', () => handleUserAssignment(task.id, user.id));
        usersList.appendChild(userEl);
    });

    // Poblar y manejar etiquetas
    // Poblar y manejar etiquetas
    const tagsList = document.getElementById('modal-tags-list');
    tagsList.innerHTML = '';

    // Obtenemos una lista única de todas las etiquetas disponibles en el tablero
    const allTags = [...new Map(currentBoardData.tasks.flatMap(t => t.tags).map(item => [item['id'], item])).values()];
    const assignedTagIds = new Set(task.tags.map(t => t.id));

    allTags.forEach(tag => {
        const tagEl = document.createElement('div');
        tagEl.className = 'list-item';

        // Creamos la "píldora" de la etiqueta para mostrarla
        const tagPill = document.createElement('span');
        tagPill.className = 'tag-pill';
        tagPill.style.backgroundColor = tag.color;
        tagPill.textContent = tag.name;
        tagEl.appendChild(tagPill);

        // Si está asignada, la marcamos como seleccionada
        if (assignedTagIds.has(tag.id)) {
            tagEl.classList.add('selected');
        }

        // Añadimos el listener para asignar/desasignar
        tagEl.addEventListener('click', () => {
            const isAssigned = assignedTagIds.has(tag.id);
            handleTagAssignment(task.id, tag.id, isAssigned);
        });

        tagsList.appendChild(tagEl);
    });

    // Mostrar el modal
    document.getElementById('modal-backdrop').style.display = 'block';
    document.getElementById('task-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('modal-backdrop').style.display = 'none';
    document.getElementById('task-modal').style.display = 'none';
}

async function handleUserAssignment(taskId, userId) {
    const task = currentBoardData.tasks.find(t => t.id === taskId);
    const newUserId = (task.assigned_user && task.assigned_user.id === userId) ? null : userId;

    await updateTask(taskId, { assigned_user_id: newUserId });

    // Recargamos todo para ver los cambios reflejados
    await fetchAndRenderBoard(PROJECT_CODE);

    // Volvemos a abrir el modal para ver el cambio instantáneo
    openTaskModal(taskId);
}

async function handleTagAssignment(taskId, tagId, isCurrentlyAssigned) {
    const url = `/api/tasks/${taskId}/tags` + (isCurrentlyAssigned ? `/${tagId}` : '');
    const method = isCurrentlyAssigned ? 'DELETE' : 'POST';

    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' },
    };

    if (method === 'POST') {
        options.body = JSON.stringify({ tag_id: tagId });
    }

    try {
        const response = await fetch(url, options);
        if (!response.ok) throw new Error('Falló la asignación de la etiqueta.');

        console.log(`Asignación de etiqueta para tarea ${taskId} actualizada.`);

        // Recargamos los datos y reabrimos el modal para ver el cambio
        await fetchAndRenderBoard(PROJECT_CODE);
        openTaskModal(taskId);

    } catch (error) {
        console.error("Error en la asignación de etiqueta:", error);
        alert("No se pudo modificar la etiqueta.");
    }
}

// --- Funciones para FILTROS ---
function renderFilters(data) {
    const filterContainer = document.getElementById('filter-container');
    filterContainer.innerHTML = '';

    // Botón para limpiar filtros
    const clearBtn = document.createElement('button');
    clearBtn.className = 'filter-btn';
    clearBtn.textContent = 'Mostrar Todo';
    clearBtn.addEventListener('click', () => {
        activeFilters = { userId: null, tagId: null };
        document.querySelectorAll('.filter-btn.active').forEach(b => b.classList.remove('active'));
        applyFilters();
    });
    filterContainer.appendChild(clearBtn);

    // Filtros de Usuario
    const allUsers = [...new Map(data.tasks.flatMap(t => t.assigned_user ? [t.assigned_user] : []).map(item => [item['id'], item])).values()];
    allUsers.forEach(user => {
        const userBtn = document.createElement('button');
        userBtn.className = 'filter-btn';
        userBtn.innerHTML = `<div class="user-avatar" title="${user.username}">${user.username.charAt(0).toUpperCase()}</div> ${user.username}`;
        userBtn.addEventListener('click', () => {
            activeFilters.userId = activeFilters.userId === user.id ? null : user.id;
            applyFilters();
        });
        filterContainer.appendChild(userBtn);
    });

    // Filtros de Etiquetas
    const allTags = [...new Map(data.tasks.flatMap(t => t.tags).map(item => [item['id'], item])).values()];
    allTags.forEach(tag => {
        const tagBtn = document.createElement('button');
        tagBtn.className = 'filter-btn';
        tagBtn.innerHTML = `<span class="tag-pill" style="background-color:${tag.color}; color:white;">${tag.name}</span>`;
        tagBtn.addEventListener('click', () => {
            activeFilters.tagId = activeFilters.tagId === tag.id ? null : tag.id;
            applyFilters();
        });
        filterContainer.appendChild(tagBtn);
    });
}

function applyFilters() {
    // Actualizamos la apariencia de los botones de filtro
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    if (activeFilters.userId) {
        // Lógica para encontrar y marcar el botón de usuario activo
    }
    // (Lógica similar para el botón de tag activo)

    // Iteramos sobre TODAS las tarjetas en el DOM
    document.querySelectorAll('.kanban-card').forEach(card => {
        const taskId = parseInt(card.getAttribute('data-task-id'));
        const task = currentBoardData.tasks.find(t => t.id === taskId);

        let show = true; // Asumimos que la tarjeta es visible por defecto

        // Comprobamos el filtro de usuario
        if (activeFilters.userId && (!task.assigned_user || task.assigned_user.id !== activeFilters.userId)) {
            show = false;
        }

        // Comprobamos el filtro de etiqueta
        if (activeFilters.tagId && !task.tags.some(tag => tag.id === activeFilters.tagId)) {
            show = false;
        }

        // Aplicamos o quitamos la clase .hidden
        if (show) {
            card.classList.remove('hidden');
        } else {
            card.classList.add('hidden');
        }
    });
}