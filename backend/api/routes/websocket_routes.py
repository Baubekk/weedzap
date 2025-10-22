#This file is only responsible for the websocket CONNECTION routes

from fastapi import WebSocket, WebSocketDisconnect
from backend.api.internal.ac_framework import inject
from backend.api.main import weedzap
from backend.api.services.websocket_service import WebsocketService

fastapi = weedzap.get_fastapi()

@fastapi.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, websocket_service: WebsocketService = inject(weedzap, WebsocketService)):
    if not await websocket_service.connect(websocket):
        return
    try:
        while True:
            data: dict = await websocket.receive_json()
            msg_type = data.get("type")
            
    except WebSocketDisconnect:
        await websocket_service.disconnect()