# Guía Rápida de Instalación - Proyecto DUBSS

Esta guía contiene los pasos necesarios para que cualquier desarrollador pueda levantar el entorno de desarrollo local del **Sistema Inteligente de Gestión Deportiva (DUBSS)** desde cero en cuestión de minutos.

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalados los siguientes programas en tu computadora:
- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**: (Obligatorio) Asegúrate de que esté abierto y el motor (*Engine*) esté corriendo.
- **Git**: Para el control de versiones.
- *(Opcional)* **Make**: Si estás en Linux/Mac ya lo tienes. Si estás en Windows, puedes instalarlo o usar los comandos completos de Docker adjuntos abajo.

---

## 🚀 Pasos para levantar el proyecto

Abre tu terminal en la carpeta raíz del proyecto (`dubss-main`) y ejecuta los siguientes pasos en orden:

### 1. Configurar Variables de Entorno
Crea el archivo `.env` copiando la plantilla. (No necesitas llenar las APIs externas para pruebas básicas).
- **Windows:**
  ```bash
  copy .env.example .env
  ```
- **Linux/Mac:**
  ```bash
  cp .env.example .env
  ```

### 2. Construir y Levantar los Contenedores
Este comando descargará las imágenes necesarias (PostgreSQL, Node, Python) y levantará el Backend y Frontend.
```bash
docker compose -f docker-compose.dev.yml up -d --build
```
*(Espera a que todos los contenedores muestren el estado `Started` o `Healthy`).*

### 3. Preparar la Base de Datos (Migraciones)
Genera las estructuras de las tablas de los módulos en base a los modelos de Django:
```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py makemigrations users deportes instalaciones fixture ml notificaciones reportes
```

Aplica estas estructuras a la base de datos PostgreSQL:
```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate
```

### 4. Crear el Usuario Administrador
Crea un usuario para poder acceder al panel de control de Django:
```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
```
*(Te pedirá ingresar un username, email y password. Nota: La contraseña no se verá en pantalla al escribirla).*

---

## 🌐 Enlaces de Acceso

Una vez completados los pasos anteriores, el proyecto estará funcionando. Puedes acceder mediante tu navegador:

| Servicio | Enlace |
|----------|--------|
| **App (Frontend Next.js)** | [http://localhost:3000](http://localhost:3000) |
| **Panel Admin (Django)** | [http://localhost:8000/admin/](http://localhost:8000/admin/) |
| **Documentación API (Swagger)** | [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) |

---

## 🛑 Comandos Útiles para el Día a Día

- **Apagar el proyecto:**
  ```bash
  docker compose -f docker-compose.dev.yml down
  ```
- **Ver logs (errores) en tiempo real:**
  ```bash
  docker compose -f docker-compose.dev.yml logs -f
  ```
- **Si usas `Makefile`**, puedes simplificar tu vida así:
  - Levantar: `make up`
  - Apagar: `make down`
  - Migrar: `make migrate`
