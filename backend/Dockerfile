FROM python:3.12-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias del sistema (psycopg2, Pillow, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Código fuente
COPY . .

# Carpetas de archivos estáticos y media
RUN mkdir -p /app/staticfiles /app/mediafiles

# Usuario no-root por seguridad
RUN addgroup --system dubss && adduser --system --ingroup dubss dubss
RUN chown -R dubss:dubss /app
USER dubss

EXPOSE 8000
