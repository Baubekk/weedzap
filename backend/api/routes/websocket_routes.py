from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.handler_service import HandlerService
from ..services.laser_service import LaserService
from ..services.movement_service import MovementService
from ..services.singleton_websocket_service import WebsocketService
from ..services.camera_service import CameraService
from ..internal.ac_framework import inject

from ..services.services import websocket_service, laser_service, movement_service, camera_service

router = APIRouter()

handler_services: Dict[str, HandlerService] = {}

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket
):
    await websocket_service.connect(websocket)
    print(f"Client connected: {websocket.client}")
    
    await camera_service.start_stream()

    try:
        while True:
            data: dict = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type == "laser":
                response = await laser_service.handle(data.get("data"))
                if response is not None:
                    await websocket.send_json(response)
            elif msg_type == "movement":
                response = await movement_service.handle(data.get("data"))
                if response is not None:
                    await websocket.send_json(response)
            
    except WebSocketDisconnect:
        await websocket_service.disconnect()
        print(f"Client disconnected: {websocket.client}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await camera_service.stop_stream()
        await websocket_service.disconnect()