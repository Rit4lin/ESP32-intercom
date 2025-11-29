import asyncio
import json
import websockets

CLIENTS = set()

async def handler(websocket):
    print("Cliente conectado:", websocket.remote_address)
    CLIENTS.add(websocket)

    try:
        async for message in websocket:
            data = json.loads(message)
            print("Mensaje recibido:", data)

            # Reenviar a todos (esp32 <-> Home Assistant)
            for client in CLIENTS:
                if client != websocket:
                    await client.send(message)

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        CLIENTS.remove(websocket)
        print("Cliente desconectado")

async def main():
    print("Servidor WebRTC/Signaling en puerto 8099")
    async with websockets.serve(handler, "0.0.0.0", 8099):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
