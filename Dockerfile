FROM python:3.13-slim

# 1. Instalar dependencias nativas del sistema (C++) para LevelDB
RUN apt-get update && apt-get install -y \
    build-essential \
    libleveldb-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Copiar requerimientos e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiar el resto del código
COPY . .

# Exponer el puerto de tu Flask (nodo_l1.py)
EXPOSE 5000

# Ejecutar el nodo
CMD ["python", "nodo_l1.py"]
