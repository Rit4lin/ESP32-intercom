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
        return {
            "esp32_host": "192.168.1.141",
            "port_in": 5001,
            "port_out": 5002,
        }
    with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

opts = load_options()
ESP32_HOST = opts.get("esp32_host", "192.168.1.141")
PORT_IN = int(opts.get("port_in", 5001))
PORT_OUT = int(opts.get("port_out", 5002))
WS_PORT = 8099

print("[INFO] Configuración:")
print("  ESP32_HOST:", ESP32_HOST)
print("  PORT_IN   :", PORT_IN)
print("  PORT_OUT  :", PORT_OUT)
print("  WS_PORT   :", WS_PORT)

sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_in.bind(("0.0.0.0", PORT_IN))

sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

clients = set()
loop = asyncio.get_event_loop()

async def broadcast_to_clients(data: bytes):
    if not clients:
        return
    broken = []
    for ws in clients:
        try:
            await ws.send(data)
        except:
            broken.append(ws)
    for ws in broken:
        clients.discard(ws)

def udp_receiver_thread():
    print(f"[INFO] Recibiendo audio desde ESP32 en UDP {PORT_IN}")
    while True:
        try:
            data, _ = sock_in.recvfrom(2048)
            asyncio.run_coroutine_threadsafe(
                broadcast_to_clients(data),
                loop
            )
        except Exception as e:
            print("[ERROR] UDP receiver:", e)

async def ws_handler(websocket, path):
    print("[INFO] Cliente WebSocket conectado")
    clients.add(websocket)
    try:
        async for message in websocket:
            if isinstance(message, (bytes, bytearray)):
                try:
                    sock_out.sendto(message, (ESP32_HOST, PORT_OUT))
                except Exception as e:
                    print("[ERROR] Envío a ESP32:", e)
            else:
                print("[WS] Mensaje no-binario:", message)
    except:
        print("[INFO] Cliente WS desconectado")
    finally:
        clients.discard(websocket)

def main():
    t = threading.Thread(target=udp_receiver_thread, daemon=True)
    t.start()

    start_server = websockets.serve(ws_handler, "0.0.0.0", WS_PORT, max_size=None)

    print(f"[INFO] Servidor WebSocket en puerto {WS_PORT}")
    loop.run_until_complete(start_server)
    loop.run_forever()

if __name__ == "__main__":
    main()

