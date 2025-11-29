import asyncio
import json
import socket
import threading
from pathlib import Path

import websockets

OPTIONS_PATH = Path("/data/options.json")

# Leemos la configuración del add-on
def load_options():
    if not OPTIONS_PATH.exists():
        print("[WARN] options.json no encontrado, usando valores por defecto")
        return {
            "esp32_host": "192.168.1.50",
            "port_in": 5001,
            "port_out": 5002,
        }
    with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

opts = load_options()
ESP32_HOST = opts.get("esp32_host", "192.168.1.50")
PORT_IN = int(opts.get("port_in", 5001))   # ESP32 -> HA
PORT_OUT = int(opts.get("port_out", 5002)) # HA -> ESP32
WS_PORT = 8099

print("[INFO] Configuración:")
print("  ESP32_HOST:", ESP32_HOST)
print("  PORT_IN   :", PORT_IN, "(ESP32 -> HA)")
print("  PORT_OUT  :", PORT_OUT, "(HA -> ESP32)")
print("  WS_PORT   :", WS_PORT, "(WebSocket HA <-> Cliente)")

# Sockets UDP
sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_in.bind(("0.0.0.0", PORT_IN))

sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Conexiones WebSocket (clientes, normalmente 1)
clients = set()
loop = asyncio.get_event_loop()


async def broadcast_to_clients(data: bytes):
    """Envía audio recibido del ESP32 a todos los clientes WebSocket."""
    if not clients:
        return
    to_remove = []
    for ws in clients:
        try:
            await ws.send(data)
        except Exception as e:
            print("[WARN] Error enviando a cliente:", e)
            to_remove.append(ws)
    for ws in to_remove:
        clients.discard(ws)


def udp_receiver_thread():
    """Hilo que recibe audio del ESP32 por UDP y lo reenvía al navegador."""
    print(f"[INFO] Escuchando audio desde ESP32 en UDP {PORT_IN}")
    while True:
        try:
            data, addr = sock_in.recvfrom(2048)
            # Aquí "data" es un chunk de audio PCM del ESP32
            # Lo mandamos al loop asyncio para que se envíe por WebSocket
            asyncio.run_coroutine_threadsafe(
                broadcast_to_clients(data),
                loop
            )
        except Exception as e:
            print("[ERROR] UDP receiver:", e)


async def ws_handler(websocket, path):
    """Maneja conexión WebSocket con el navegador / app."""
    print("[INFO] Cliente WebSocket conectado")
    clients.add(websocket)
    try:
        async for message in websocket:
            # Si el mensaje es binario: audio desde el micro del móvil
            if isinstance(message, (bytes, bytearray)):
                # Lo mandamos al ESP32 por UDP (HA -> ESP32)
                try:
                    sock_out.sendto(message, (ESP32_HOST, PORT_OUT))
                except Exception as e:
                    print("[ERROR] Enviando audio a ESP32:", e)
            else:
                # Si es texto, podría ser control/estado, de momento lo ignoramos
                try:
                    data = json.loads(message)
                    print("[WS] Mensaje de control:", data)
                except Exception:
                    print("[WS] Texto recibido:", message)
    except websockets.exceptions.ConnectionClosed:
        print("[INFO] Cliente WebSocket desconectado")
    finally:
        clients.discard(websocket)


def main():
    # Lanzamos hilo de recepción UDP
    t = threading.Thread(target=udp_receiver_thread, daemon=True)
    t.start()

    # Lanzamos servidor WebSocket
    start_server = websockets.serve(ws_handler, "0.0.0.0", WS_PORT, max_size=None)

    print(f"[INFO] Servidor WebSocket escuchando en puerto {WS_PORT}")
    loop.run_until_complete(start_server)
    loop.run_forever()


if __name__ == "__main__":
    main()
