from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect
from backend.api.internal.ac_framework import inject
from backend.api.main import weedzap
from backend.api.services.handler_service import HandlerService
from backend.api.services.laser_service import LaserService
from backend.api.services.movement_service import MovementService
from backend.api.services.websocket_service import WebsocketService

fastapi = weedzap.get_fastapi()

handler_services: Dict[str, HandlerService] = {
    "laser": weedzap.get_context().get_component(LaserService),
    "movement": weedzap.get_context().get_component(MovementService)
}

@fastapi.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, websocket_service: WebsocketService = inject(weedzap, WebsocketService)):
    if not await websocket_service.connect(websocket):
        return
    try:
        while True:
            data: dict = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type in handler_services:
                response = await handler_services[msg_type].handle(data.get("data"))
                if response is not None:
                    await websocket.send_json(response)
            
    except WebSocketDisconnect:
        await websocket_service.disconnect()