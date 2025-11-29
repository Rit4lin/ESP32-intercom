FROM python:3.11-slim

WORKDIR /app

COPY server.py /app/server.py
COPY run.sh /app/run.sh

RUN chmod +x /app/run.sh

EXPOSE 8123
EXPOSE 8765/udp

CMD ["/app/run.sh"]
