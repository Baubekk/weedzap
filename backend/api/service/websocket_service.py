from fastapi import WebSocket, WebSocketDisconnect
import asyncio

class WebsocketService:
    def __init__(self):
        self.active_connection: WebSocket | None = None
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        async with self.lock:
            if self.active_connection is not None:
                return False
            self.active_connection = websocket
            return True

    async def disconnect(self):
        async with self.lock:
            self.active_connection = None

def get_websocket_service():
    return WebsocketService()