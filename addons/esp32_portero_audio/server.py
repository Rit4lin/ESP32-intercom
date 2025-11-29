import asyncio
import websockets
import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 8765

WS_PORT = 8123

# Socket UDP para enviar audio al ESP32
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ESP32_IP = "192.168.1.141"     # tu ESP32
ESP32_UDP_PORT = 8765          # puerto de escucha del ESP32

connected_clients = set()


async def ws_handler(websocket, path):
    print("Cliente WebSocket conectado")
    connected_clients.add(websocket)

    try:
        async for message in websocket:
            # Audio PCM recibido del ESP32 → HA
            udp_sock.sendto(message, (ESP32_IP, ESP32_UDP_PORT))

    except Exception as e:
        print("Error WS:", e)

    finally:
        connected_clients.remove(websocket)
        print("Cliente desconectado")


async def udp_listener():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind((UDP_IP, UDP_PORT))

    print("Servidor UDP escuchando en puerto", UDP_PORT)

    while True:
        data, addr = udp.recvfrom(2048)

        # Reenviar audio entrante hacia HA por WebSocket
        websockets_to_remove = []

        for client in connected_clients:
            try:
                await client.send(data)
            except:
                websockets_to_remove.append(client)

        for c in websockets_to_remove:
            connected_clients.remove(c)


async def main():
    print("Servidor WS en puerto", WS_PORT)

    ws_server = websockets.serve(ws_handler, "0.0.0.0", WS_PORT)
    udp_task = asyncio.create_task(udp_listener())

    await asyncio.gather(ws_server, udp_task)


asyncio.run(main())
