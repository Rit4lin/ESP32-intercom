ARG BUILD_FROM=ghcr.io/hassio-addons/base:13.2.2
FROM ${BUILD_FROM}

# Instalar Python3
RUN apk add --no-cache python3 py3-pip

WORKDIR /app

COPY server.py /app/server.py
COPY run.sh /app/run.sh

RUN chmod +x /app/run.sh

EXPOSE 8099

CMD [ "/app/run.sh" ]
