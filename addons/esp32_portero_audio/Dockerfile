FROM python:3.11-slim

# Crear carpeta del servidor
WORKDIR /app

# Instalar dependencias
RUN pip install websockets

# Copiar archivos del addon
COPY server.py /app/server.py
COPY run.sh /app/run.sh

# Dar permisos de ejecución
RUN chmod +x /app/run.sh

EXPOSE 8123/tcp
EXPOSE 8765/udp

CMD ["/app/run.sh"]
