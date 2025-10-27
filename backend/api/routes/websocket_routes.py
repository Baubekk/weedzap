from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect, Depends, APIRouter
from backend.api.internal.ac_framework import inject, component
from backend.api.main import weedzap
from backend.api.services.handler_service import HandlerService
from backend.api.services.laser_service import LaserService
from backend.api.services.movement_service import MovementService
from backend.api.services.websocket_service import WebsocketService
from backend.api.services.camera_service import CameraService

router = APIRouter()

handler_services: Dict[str, HandlerService] = {
    "laser": weedzap.get_context().get_component(LaserService),
    "movement": weedzap.get_context().get_component(MovementService)
}

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    websocket_service: WebsocketService = Depends(weedzap.get(WebsocketService)),
    laser_service: LaserService = Depends(weedzap.get(LaserService)),
    movement_service: MovementService = Depends(weedzap.get(MovementService)),
    camera_service: CameraService = Depends(weedzap.get(CameraService))
):
    await websocket_service.connect(websocket)
    print(f"Client connected: {websocket.client}")
    
    await camera_service.start_stream()

    try:
        # while True:
        #     data: dict = await websocket.receive_json()
        #     msg_type = data.get("type")
        #     if msg_type == "laser_command":
        #         command = data.get("command")
        #         if command == "on":
        #             laser_service.turn_on()
        #             await websocket_service.send({"status": "laser_on"})
        #         elif command == "off":
        #             laser_service.turn_off()
        #             await websocket_service.send({"status": "laser_off"})
        #     elif msg_type == "movement_command":
        #         direction = data.get("direction")
        #         speed = data.get("speed", 0.5)
        #         if direction == "forward":
        #             movement_service.move_forward(speed)
        #         elif direction == "backward":
        #             movement_service.move_backward(speed)
        #         elif direction == "left":
        #             movement_service.turn_left(speed)
        #         elif direction == "right":
        #             movement_service.turn_right(speed)
        #         elif direction == "stop":
        #             movement_service.stop()
        #         await websocket_service.send({"status": f"movement_{direction}"})
        #     else:
        #         await websocket_service.send({"error": "Unknown message type"})
        pass
            
    except WebSocketDisconnect:
        print(f"Client disconnected: {websocket.client}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await camera_service.stop_stream()
        await websocket_service.disconnect(websocket)