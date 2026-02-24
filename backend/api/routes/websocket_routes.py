from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.handler_service import HandlerService
from ..services.laser_service import LaserService
from ..services.movement_service import MovementService
from ..services.singleton_websocket_service import WebsocketService
from ..services.camera_service import CameraService
from ..internal.ac_framework import inject

from ..services.services import websocket_service, laser_service, movement_service, camera_service, config_service, arduino_service
from ..services.config_service import ConfigService

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
                if command == "tool_on":
                    tool_number = command_data.get("tool_number")
                    if tool_number is not None:
                        try:
                            tool_number = int(tool_number)
                            success, message = await laser_service.tool_on(tool_number)
                            if success:
                                await websocket.send_json({"type": "laser_ack", "command": command, "status": "success", "message": message})
                            else:
                                await websocket.send_json({"type": "laser_ack", "command": command, "status": "error", "message": message})
                        except ValueError:
                            await websocket.send_json({"type": "laser_ack", "command": command, "status": "error", "message": "Invalid integer value for tool_number"})
                    else:
                        await websocket.send_json({"type": "laser_ack", "command": command, "status": "error", "message": "Missing tool_number for tool_on"})
                elif command == "tool_off":
                    success, message = await laser_service.tool_off()
                    if success:
                        await websocket.send_json({"type": "laser_ack", "command": command, "status": "success", "message": message})
                    else:
                        await websocket.send_json({"type": "laser_ack", "command": command, "status": "error", "message": message})
                elif command == "fire_tool":
                    value = command_data.get("value")
                    if value is not None:
                        success, message = await laser_service.fire_tool(value)
                        if success:
                            await websocket.send_json({"type": "laser_ack", "command": command, "status": "success", "message": message})
                        else:
                            await websocket.send_json({"type": "laser_ack", "command": command, "status": "error", "message": message})
                    else:
                        await websocket.send_json({"type": "laser_ack", "command": command, "status": "error", "message": "Missing value for fire_tool"})
                elif command == "tool_status":
                    success, message = await laser_service.get_current_tool_status()
                    if success:
                        await websocket.send_json({"type": "laser_ack", "command": command, "status": "success", "message": message})
                    else:
                        await websocket.send_json({"type": "laser_ack", "command": command, "status": "error", "message": message})
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
                elif command == "jog":
                    dx = command_data.get("dx")
                    dy = command_data.get("dy")
                    dz = command_data.get("dz")
                    if all(v is not None for v in [dx, dy, dz]):
                        try:
                            dx = float(dx)
                            dy = float(dy)
                            dz = float(dz)
                            success, message = await movement_service.jog(dx, dy, dz)
                            if success:
                                await websocket.send_json({"type": "movement_ack", "command": command, "status": "success", "message": message})
                            else:
                                await websocket.send_json({"type": "movement_ack", "command": command, "status": "error", "message": message})
                        except ValueError:
                            await websocket.send_json({"type": "movement_ack", "command": command, "status": "error", "message": "Invalid float value for dx, dy, or dz"})
                    else:
                        await websocket.send_json({"type": "movement_ack", "command": command, "status": "error", "message": "Missing dx, dy, or dz for jog command"})
                elif command == "home":
                    success, message = await movement_service.home()
                    if success:
                        await websocket.send_json({"type": "movement_ack", "command": command, "status": "success", "message": message})
                    else:
                        await websocket.send_json({"type": "movement_ack", "command": command, "status": "error", "message": message})
                elif command == "pos":
                    success, message = await movement_service.get_current_position()
                    if success:
                        await websocket.send_json({"type": "movement_ack", "command": command, "status": "success", "position": message})
                    else:
                        await websocket.send_json({"type": "movement_ack", "command": command, "status": "error", "message": message})
                elif command == "status":
                    success, message = await movement_service.get_status()
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
                    # Integer parameters
                    if param_name in ["LED_PIN_STATE"]:
                        try:
                            value = int(param_value)
                            if param_name == "LED_PIN_STATE":
                                config_service.set_led_state(value)
                            await websocket.send_json({"type": "config_ack", "param": param_name, "value": value, "status": "success"})
                        except ValueError:
                            await websocket.send_json({"type": "config_ack", "param": param_name, "value": param_value, "status": "error", "message": "Invalid integer value"})
                    # Float parameters
                    elif param_name in ["steps_x", "steps_y", "steps_z", "x_max_l", "y_max_l", "z_max_l", "h_spd_x", "h_spd_y", "h_spd_z", "homing_speed_slow", "max_speed", "accel"]:
                        try:
                            value = float(param_value)
                            if param_name == "steps_x":
                                config_service.set_steps_x(value)
                            elif param_name == "steps_y":
                                config_service.set_steps_y(value)
                            elif param_name == "steps_z":
                                config_service.set_steps_z(value)
                            elif param_name == "x_max_l":
                                config_service.set_x_max_l(value)
                            elif param_name == "y_max_l":
                                config_service.set_y_max_l(value)
                            elif param_name == "z_max_l":
                                config_service.set_z_max_l(value)
                            elif param_name == "h_spd_x":
                                config_service.set_h_spd_x(value)
                            elif param_name == "h_spd_y":
                                config_service.set_h_spd_y(value)
                            elif param_name == "h_spd_z":
                                config_service.set_h_spd_z(value)
                            elif param_name == "homing_speed_slow":
                                config_service.set_homing_speed_slow(value)
                            elif param_name == "max_speed":
                                config_service.set_max_speed(value)
                            elif param_name == "accel":
                                config_service.set_accel(value)
                            await websocket.send_json({"type": "config_ack", "param": param_name, "value": value, "status": "success"})
                        except ValueError:
                            await websocket.send_json({"type": "config_ack", "param": param_name, "value": param_value, "status": "error", "message": "Invalid float value"})
                    else:
                        await websocket.send_json({"type": "config_ack", "param": param_name, "status": "error", "message": "Unknown configuration parameter"})
                else:
                    await websocket.send_json({"type": "config_ack", "status": "error", "message": "Missing param or value"})

            elif msg_type == "led":
                command = data.get("command")
                command_data = data.get("data", {})
                if command == "set_state":
                    state = command_data.get("state")
                    if state is not None:
                        try:
                            state = int(state)
                            if state in [0, 1]:
                                success, message = arduino_service.send_led_command(state)
                                if success:
                                    await websocket.send_json({"type": "led_ack", "command": command, "status": "success", "message": message})
                                else:
                                    await websocket.send_json({"type": "led_ack", "command": command, "status": "error", "message": message})
                            else:
                                await websocket.send_json({"type": "led_ack", "command": command, "status": "error", "message": "State must be 0 or 1"})
                        except ValueError:
                            await websocket.send_json({"type": "led_ack", "command": command, "status": "error", "message": "Invalid integer value for state"})
                    else:
                        await websocket.send_json({"type": "led_ack", "command": command, "status": "error", "message": "Missing state for set_state command"})
                else:
                    await websocket.send_json({"type": "led_ack", "command": command, "status": "error", "message": "Unknown led command"})
            
            elif msg_type == "raw":
                command = data.get("command")
                if command is not None:
                    success, message = arduino_service.send_command(command)
                    if success:
                        await websocket.send_json({"type": "raw_ack", "command": command, "status": "success", "message": message})
                    else:
                        await websocket.send_json({"type": "raw_ack", "command": command, "status": "error", "message": message})
                else:
                    await websocket.send_json({"type": "raw_ack", "status": "error", "message": "Missing command for raw command"})
            
    except WebSocketDisconnect:
        await websocket_service.disconnect()
        print(f"Client disconnected: {websocket.client}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await camera_service.stop_stream()
        await websocket_service.disconnect()