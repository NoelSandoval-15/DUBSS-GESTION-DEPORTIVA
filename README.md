# DUBSS — Sistema Inteligente de Gestión Deportiva

**Universidad Autónoma Gabriel René Moreno — FICCT**

## Inicio rápido (3 comandos)

```bash
# 1. Copiar variables de entorno
copy .env.example .env

# 2. Levantar todo
docker compose -f docker-compose.dev.yml up -d --build

# 3. Migraciones y superusuario
docker compose -f docker-compose.dev.yml exec backend python manage.py makemigrations users deportes instalaciones fixture ml notificaciones reportes
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate
docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
```

## URLs del sistema

| Servicio     | URL                             |
| ------------ | ------------------------------- |
| Frontend     | http://localhost:3000           |
| API REST     | http://localhost:8000/api/v1/   |
| Swagger UI   | http://localhost:8000/api/docs/ |
| Admin Django | http://localhost:8000/admin/    |

## Stack

- **Backend**: Django 5 + DRF + JWT + Swagger
- **Frontend**: Next.js 14 + React 18 + TypeScript + Tailwind
- **Base de datos**: PostgreSQL 16
- **ML**: scikit-learn (RandomForest)
- **Docker**: Docker Compose

## Equipo

ALDANA CLAURE BRAYAN

SANDOVAL MARTINEZ ERICK NOEL 

Materia: Taller de Grado INF511 — FICCT, UAGRM
