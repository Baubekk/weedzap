from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from ..internal.ac_framework import component, inject

@component
class WebsocketService:
    def __init__(self):
        self.active_connection: WebSocket | None = None
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> bool:
        raise Exception("suka")
        async with self.lock:
            if self.active_connection is not None:
                return False
            self.active_connection = websocket
            websocket.accept()
            return True

    async def disconnect(self):
        async with self.lock:
            self.active_connection = None

    async def send(self, data: dict):
        async with self.lock:
            if self.active_connection is not None:
                await self.active_connection.send_json(data)
        return
