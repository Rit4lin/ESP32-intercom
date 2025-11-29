ARG BUILD_FROM=ghcr.io/home-assistant/{arch}-base:latest
FROM ${BUILD_FROM}

# Instalamos Python y dependencias
RUN apk add --no-cache python3 py3-pip

# Instalamos librería websockets para el servidor
RUN pip3 install --no-cache-dir websockets

# Copiamos el código del add-on
COPY server.py /server.py
COPY run.sh /run.sh

# Damos permisos de ejecución al script de arranque
RUN chmod a+x /run.sh

# Comando por defecto del contenedor
CMD ["/run.sh"]
