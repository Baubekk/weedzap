from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.handler_service import HandlerService
from ..services.laser_service import LaserService
from ..services.movement_service import MovementService
from ..services.singleton_websocket_service import WebsocketService
from ..services.camera_service import CameraService
from ..internal.ac_framework import inject

from ..services.services import websocket_service, laser_service, movement_service, camera_service, config_service
from ..services.config_service import ConfigService, MovementMode, LaserState
from ..services.laser_service import ToolMode

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
                command = data.get("command")
                command_data = data.get("data", {})
                if command == "set_tool_mode":
                    tool_mode_str = command_data.get("tool_mode")
                    if tool_mode_str == "laser":
                        tool_mode = ToolMode.LASER
                    elif tool_mode_str == "servo":
                        tool_mode = ToolMode.SERVO
                    else:
                        await websocket.send_json({"type": "laser_ack", "command": command, "status": "error", "message": "Invalid tool mode"})
                        continue
                    await laser_service.set_tool_mode(tool_mode)
                    await websocket.send_json({"type": "laser_ack", "command": command, "status": "success"})
                elif command == "fire_tool":
                    value = command_data.get("value")
                    if value is not None:
                        response = await laser_service.fire_tool(value)
                        if response is not None and "error" in response:
                             await websocket.send_json({"type": "laser_ack", "command": command, "status": "error", "message": response["error"]})
                        else:
                             await websocket.send_json({"type": "laser_ack", "command": command, "status": "success"})
                    else:
                        await websocket.send_json({"type": "laser_ack", "command": command, "status": "error", "message": "Missing value for fire_tool"})
                elif command == "stop_tool":
                    await laser_service.stop_tool()
                    await websocket.send_json({"type": "laser_ack", "command": command, "status": "success"})
                else:
                    await websocket.send_json({"type": "laser_ack", "command": command, "status": "error", "message": "Unknown laser command"})

            elif msg_type == "movement":
                command = data.get("command")
                command_data = data.get("data", {})
                if command == "move":
                    x = command_data.get("x")
                    y = command_data.get("y")
                    z = command_data.get("z")
                    if all(v is not None for v in [x, y, z]):
                        success, message = await movement_service.move(x, y, z)
                        if success:
                            await websocket.send_json({"type": "movement_ack", "command": command, "status": "success", "message": message})
                        else:
                            await websocket.send_json({"type": "movement_ack", "command": command, "status": "error", "message": message})
                    else:
                        await websocket.send_json({"type": "movement_ack", "command": command, "status": "error", "message": "Missing x, y, or z for move command"})
                elif command == "home":
                    success, message = await movement_service.home()
                    if success:
                        await websocket.send_json({"type": "movement_ack", "command": command, "status": "success", "message": message})
                    else:
                        await websocket.send_json({"type": "movement_ack", "command": command, "status": "error", "message": message})
                else:
                    await websocket.send_json({"type": "movement_ack", "command": command, "status": "error", "message": "Unknown movement command"})
            elif msg_type == "config":
                param_name = data.get("param")
                param_value = data.get("value")
                if param_name and param_value is not None:
                    if param_name in ["steps_x", "steps_y", "steps_z", "limit_x", "limit_y", "limit_z"]:
                        try:
                            value = int(param_value)
                            config_service.unsafe_set(param_name, value)
                            config_service._apply_config_to_arduino() # Apply changes to Arduino
                            await websocket.send_json({"type": "config_ack", "param": param_name, "value": value, "status": "success"})
                        except ValueError:
                            await websocket.send_json({"type": "config_ack", "param": param_name, "value": param_value, "status": "error", "message": "Invalid integer value"})
                    elif param_name in ["max_speed", "accel"]:
                        try:
                            value = float(param_value)
                            # Use specific setters for max_speed and accel to ensure Arduino commands are sent
                            if param_name == "max_speed":
                                config_service.set_speed(value)
                            elif param_name == "accel":
                                config_service.set_acceleration(value)
                            await websocket.send_json({"type": "config_ack", "param": param_name, "value": value, "status": "success"})
                        except ValueError:
                            await websocket.send_json({"type": "config_ack", "param": param_name, "value": param_value, "status": "error", "message": "Invalid float value"})
                    else:
                        await websocket.send_json({"type": "config_ack", "param": param_name, "status": "error", "message": "Unknown configuration parameter"})
                else:
                    await websocket.send_json({"type": "config_ack", "status": "error", "message": "Missing param or value"})
            
    except WebSocketDisconnect:
        await websocket_service.disconnect()
        print(f"Client disconnected: {websocket.client}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await camera_service.stop_stream()
        await websocket_service.disconnect()