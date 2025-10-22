from fastapi import WebSocket, WebSocketDisconnect
import asyncio

from backend.api.internal.ac_framework import component
from backend.api.main import weedzap

@component(weedzap)
class WebsocketService:
    def __init__(self):
        self.active_connection: WebSocket | None = None
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> bool:
        async with self.lock:
            if self.active_connection is not None:
                return False
            self.active_connection = websocket
            return True

    async def disconnect(self):
        async with self.lock:
            self.active_connection = None

    async def send(self, data: dict):
        async with self.lock:
            if self.active_connection is not None:
                await self.active_connection.send_json(data)
        return