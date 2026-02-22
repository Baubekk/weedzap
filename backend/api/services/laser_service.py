from enum import Enum
from ..internal.ac_framework import component, inject
from .arduino_service import ArduinoService
from .config_service import ConfigService
from .handler_service import HandlerService

class LaserComponent(Enum):
    FIRING = "firing"

class ToolMode(Enum):
    LASER = "laser"
    SERVO = "servo"

#fuck the variable naming in this class (i did it myself)

@component
class LaserService:
    def __init__(self, config_service: ConfigService, arduino_service: ArduinoService):
        self.config_service = config_service
        self.arduino_service = arduino_service
        self._current_tool_mode = ToolMode.LASER

    async def set_tool_mode(self, tool_mode: ToolMode):
        if tool_mode == ToolMode.LASER:
            command = "TOOL 0"
        elif tool_mode == ToolMode.SERVO:
            command = "TOOL 1"
        else:
            return {"error": "Invalid tool mode"}
        await self.arduino_service.send(command)
        self._current_tool_mode = tool_mode

    async def fire_tool(self, value: int):
        if self._current_tool_mode == ToolMode.LASER:
            if not (0 <= value <= 255):
                return {"error": "Laser value must be between 0 and 255"}
        elif self._current_tool_mode == ToolMode.SERVO:
            if not (0 <= value <= 180):
                return {"error": "Servo value must be between 0 and 180"}
        else:
            return {"error": "Unknown tool mode"}

        command = f"FIRE {value}"
        await self.arduino_service.send(command)




    async def stop_tool(self):
        await self.arduino_service.send("STOP")

    async def firing(self, data: dict):

        if data.get("active") is True:
            await self.fire_tool(value=255)

        else:
            await self.stop_tool()



