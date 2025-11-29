FROM python:3.11-slim

WORKDIR /app

COPY server.py /app/server.py

RUN pip install --no-cache-dir websockets sounddevice numpy

EXPOSE 8099

CMD ["python3", "/app/server.py"]
