import asyncio
import websockets

connected_clients = set()


async def handle_client(websocket):
    print(f"Client connected from {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received: {message}")
            disconnected = set()
            for client in connected_clients:
                if client is websocket:
                    continue  # don't echo a message back to whoever sent it
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            for client in disconnected:
                connected_clients.discard(client)
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket.remote_address} disconnected")
    finally:
        connected_clients.discard(websocket)


async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
