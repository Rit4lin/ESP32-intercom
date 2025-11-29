import asyncio
import websockets

WS_PORT = 8124
UDP_PORT = 8765

clients = set()


async def broadcast(data: bytes):
    """Envía los datos recibidos por UDP a todos los clientes WebSocket."""
    if not clients:
        return

    to_remove = set()
    coros = []
    for ws in clients:
        if ws.closed:
            to_remove.add(ws)
            continue
        coros.append(ws.send(data))

    for ws in to_remove:
        clients.discard(ws)

    if coros:
        await asyncio.gather(*coros, return_exceptions=True)


class UdpProtocol:
    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print(f"UDP escuchando en 0.0.0.0:{UDP_PORT}")

    def datagram_received(self, data, addr):
        # Cada datagrama que llega se reenvía por WebSocket
        asyncio.create_task(broadcast(data))

    def error_received(self, exc):
        print(f"Error UDP: {exc}")

    def connection_lost(self, exc):
        print("Conexión UDP cerrada")


async def ws_handler(websocket, path):
    """Maneja las conexiones WebSocket (solo envío de audio por ahora)."""
    print("Cliente WebSocket conectado")
    clients.add(websocket)
    try:
        async for _ in websocket:
            # Si quieres aceptar mensajes desde HA, procesa aquí
            pass
    finally:
        print("Cliente WebSocket desconectado")
        clients.discard(websocket)


async def main():
    loop = asyncio.get_running_loop()

    # Servidor WebSocket
    ws_server = await websockets.serve(ws_handler, "0.0.0.0", WS_PORT)
    print(f"WebSocket escuchando en ws://0.0.0.0:{WS_PORT}")

    # Servidor UDP
    await loop.create_datagram_endpoint(
        lambda: UdpProtocol(),
        local_addr=("0.0.0.0", UDP_PORT),
    )

    # Mantener el servicio vivo
    await ws_server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
