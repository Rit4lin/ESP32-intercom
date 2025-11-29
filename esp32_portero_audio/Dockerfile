FROM python:3.11-slim

WORKDIR /app

COPY server.py /app/server.py
COPY run.sh /app/run.sh

RUN chmod +x /app/run.sh && \
    pip install --no-cache-dir websockets numpy

EXPOSE 8099

CMD ["/app/run.sh"]
