import asyncio
import websockets

async def simple_client_listener():
    uri = "ws://0.0.0.0:59126"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print(data)

asyncio.get_event_loop().run_until_complete(simple_client_listener())