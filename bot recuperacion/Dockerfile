# ===== Build dependencies =====
FROM python:3.13-slim AS builder

WORKDIR /app

COPY requirements.txt .

# Instalar dependencias en /install para copiar al runtime
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt -t /install

# ===== Runtime =====
FROM python:3.13-slim

# Crear usuario sin privilegios
RUN useradd --create-home --shell /usr/sbin/nologin --uid 1000 botuser

WORKDIR /app

# Configuración de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/install:$PYTHONPATH

# Copiar dependencias y código, asignando propietario correcto
COPY --from=builder /install /install
COPY --chown=botuser:botuser . .

# Cambiar a usuario no root
USER botuser

CMD ["python", "main.py"]
