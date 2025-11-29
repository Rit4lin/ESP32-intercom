import asyncio
import websockets
import socket

ESP32_IP = "192.168.1.141"
ESP32_RX_PORT = 12346
ESP32_TX_PORT = 12345

clients = set()

sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_rx.bind(("0.0.0.0", ESP32_TX_PORT))

async def udp_to_ws():
    while True:
        data, _ = sock_rx.recvfrom(2048)
        for ws in list(clients):
            try:
                await ws.send(data)
            except:
                pass

async def ws_handler(websocket):
    clients.add(websocket)
    try:
        async for data in websocket:
            sock_tx.sendto(data, (ESP32_IP, ESP32_RX_PORT))
    finally:
        clients.remove(websocket)

async def main():
    print("Servidor WebSocket listo en puerto 8099")
    await asyncio.gather(
        websockets.serve(ws_handler, "0.0.0.0", 8099),
        udp_to_ws()
    )

asyncio.run(main())
