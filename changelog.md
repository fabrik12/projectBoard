# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-06-27

Esta es una versión de funcionalidades menores que introduce un completo sistema de administración para la gestión de proyectos.

### Added

- **Panel de Administración:** Se ha creado una sección `/admin` completamente nueva para la gestión de la aplicación, separada de la vista del usuario final.
- **Dashboard de Proyectos:** Una nueva vista de panel de control (`/admin/dashboard`) que lista todos los proyectos existentes en la base de datos, mostrando su ID, nombre y código de acceso.
- **Creación de Proyectos:** Desde el dashboard, el administrador ahora puede crear nuevos proyectos especificando un nombre y un código único.
- **Eliminación de Proyectos:** Se ha añadido la capacidad de eliminar proyectos existentes directamente desde el dashboard. La eliminación de un proyecto también elimina en cascada todas las tareas asociadas gracias al diseño de la base de datos.
- **Ruta de Cierre de Sesión:** Se ha añadido un endpoint `/admin/logout` para cerrar de forma segura la sesión del administrador.

### Changed

- **Estructura del Proyecto:** Se ha refactorizado la aplicación para incluir un nuevo Blueprint (`admin.py`) que encapsula toda la lógica y rutas relacionadas con la administración, manteniendo el código principal limpio y organizado.
- **Flujo de Login:** El login de administrador ahora redirige a un dashboard funcional en lugar de a una página de confirmación temporal.

### Security

- **Autenticación de Administrador:** Se ha implementado un sistema de login para el panel de administración, protegido por una clave maestra única que debe ser configurada a través de la variable de entorno `ADMIN_SECRET_KEY`.
- **Protección de Rutas con Decorador:** Se ha creado un decorador `@admin_required` para proteger todas las rutas del panel de administración, redirigiendo a los usuarios no autenticados a la página de login. Esto asegura que solo el administrador pueda acceder a las funciones de gestión.
- **Manejo de Sesiones:** Se utiliza el sistema de sesiones de Flask para mantener el estado de autenticación del administrador durante su visita.

---

## [1.1.5] - 2025-06-28

Esta es una versión de parche que expande significativamente las capacidades del Panel de Administración, permitiendo la gestión completa de los recursos utilizados en los tableros Kanban.

### Added

- **Gestión de Usuarios:** El administrador ahora puede crear y eliminar usuarios globales desde el panel de administración. Estos usuarios estarán disponibles para ser asignados a tareas en todos los tableros del proyecto.
- **Gestión de Etiquetas:** Se ha implementado la capacidad de crear nuevas etiquetas globales, especificando un nombre y un color a través de un selector. También se pueden eliminar las etiquetas existentes.
- **Nuevos Endpoints de Administración:** Se han añadido los endpoints de backend necesarios (`/admin/users/create`, `/admin/users/<id>/delete`, etc.) para soportar las operaciones CRUD sobre usuarios y etiquetas desde el panel de administración.

### Changed

- **Interfaz del Dashboard de Administración:** El dashboard principal ha sido rediseñado para usar una interfaz de pestañas (tabs), separando la gestión de Proyectos, Usuarios y Etiquetas en secciones limpias y organizadas para una mejor experiencia de usuario.
- **Carga de Datos del Dashboard:** La ruta `/admin/dashboard` ha sido actualizada para obtener no solo la lista de proyectos, sino también la lista completa de usuarios y etiquetas para poblar la nueva interfaz de pestañas.
