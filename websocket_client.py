import asyncio
import json
import websockets
import websockets.exceptions
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


# Demo user (may not work in production)
class DemoUser(BaseModel):
    api_key: str = "xxx"
    api_secret: str = "xxx"


# Creating a ThreadPoolExecutor for running input in a separate thread
executor = ThreadPoolExecutor()


async def get_input(prompt):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, input, prompt)


async def send_messages(websocket):
    while True:
        message = await get_input("")
        try:
            message_json = {
                "message": message,
                "timestamp": None,
                "target_user_id": None,
            }
            await websocket.send(json.dumps(message_json))
            print("Message sent: ", message)
        except websockets.exceptions.ConnectionClosedError:
            print("Server is not available. Exiting...")
            break


async def receive_messages(websocket):
    while True:
        response = await websocket.recv()
        print("Received: ", response)


async def websocket_client():
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")
    uri = "wss://api.princeofcrypto.com/v1/stream/signals"
    if API_KEY is None or API_SECRET is None:
        logging.warning(
            "API_KEY or API_SECRET not found in environment variables. Using demo user."
        )
        demo_user = DemoUser()
        API_KEY = demo_user.api_key
        API_SECRET = demo_user.api_secret
    headers = {"x-api-key": API_KEY, "x-api-secret": API_SECRET}

    async def async_websocket_connection(uri, headers):
        async with websockets.connect(uri, extra_headers=headers) as websocket:
            sender_task = asyncio.create_task(send_messages(websocket))
            receiver_task = asyncio.create_task(receive_messages(websocket))
            await asyncio.gather(sender_task, receiver_task)

    # Connecting with headers
    while True:
        try:
            await async_websocket_connection(uri, headers)
        except websockets.exceptions.ConnectionClosedError:
            print("Connection closed. Reconnecting in 5 sec...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(websocket_client())
# websockets.exceptions.ConnectionClosedError -> asyncio.exceptions.IncompleteReadError
