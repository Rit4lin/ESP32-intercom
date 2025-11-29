import asyncio
import websockets
import socket

# Configuración
UDP_PORT = 8765        # Puerto donde escucha HA el audio del ESP32
WS_PORT = 8123         # Puerto WebSocket para enviar audio al ESP32

clients = set()

# -------------------------------
#   Servidor UDP (RECIBIR AUDIO)
# -------------------------------
async def udp_server():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("0.0.0.0", UDP_PORT))
    print(f"[UDP] Escuchando audio en puerto {UDP_PORT}...")

    loop = asyncio.get_event_loop()

    while True:
        data, addr = await loop.run_in_executor(None, udp.recvfrom, 2048)
        print(f"[UDP] {len(data)} bytes desde {addr}")
        # Aquí podrías reenviar el audio al móvil via WebRTC en un futuro


# ----------------------------------------
#   Servidor WebSocket (ENVIAR AUDIO)
# ----------------------------------------
async def ws_handler(websocket, path):
    clients.add(websocket)
    print("[WS] Cliente conectado")

    try:
        async for message in websocket:
            # mensaje = bytes de audio enviados desde Home Assistant → ESP32
            print(f"[WS] Enviando {len(message)} bytes a ESP32...")
    except:
        pass
    finally:
        clients.remove(websocket)
        print("[WS] Cliente desconectado")


async def ws_server():
    print(f"[WS] Servidor WebSocket en puerto {WS_PORT}...")
    async with websockets.serve(ws_handler, "0.0.0.0", WS_PORT):
        await asyncio.Future()  # nunca termina


# -------------------------------
#   EJECUCIÓN PRINCIPAL
# -------------------------------
async def main():
    await asyncio.gather(
        udp_server(),
        ws_server()
    )

if __name__ == "__main__":
    print("Servidor de audio ESP32 Intercom iniciado")
    asyncio.run(main())
