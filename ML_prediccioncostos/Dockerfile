# Usar Python 3.11
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para Prophet
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY api_predictor.py .
COPY app_flask.py .
COPY modelos_join/ ./modelos_join/

# Crear carpetas para salidas
RUN mkdir -p predicciones graficas

# Exponer puerto
EXPOSE 5000

# Variable de entorno
ENV FLASK_APP=app_flask.py
ENV PORT=5000

# Comando de inicio
CMD gunicorn app_flask:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2
