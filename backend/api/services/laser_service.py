from enum import Enum
from ..internal.ac_framework import component, inject
from .arduino_service import ArduinoService
from .config_service import ConfigService
from .handler_service import HandlerService
import asyncio # Added this import

class LaserComponent(Enum):
    FIRING = "firing"



@component
class LaserService:
    def __init__(self, config_service: ConfigService, arduino_service: ArduinoService):
        self.config_service = config_service
        self.arduino_service = arduino_service
        self._current_tool_mode: int | None = None

    async def tool_on(self, tool_number: int) -> tuple[bool, str]:
        success, response = await asyncio.to_thread(self.arduino_service.send_tool_on_command, tool_number)
        if success:
            self._current_tool_mode = tool_number
        return success, response

    async def fire_tool(self, value: int) -> tuple[bool, str]:
        command = f"FIRE {value}"
        return await asyncio.to_thread(self.arduino_service.send_command, command, ["OK: Laser power set to", "OK: Servo angle set to", "ERROR:"])

    async def tool_off(self) -> tuple[bool, str]:
        success, response = await asyncio.to_thread(self.arduino_service.send_tool_off_command)
        if success:
            self._current_tool_mode = None
        return success, response

    async def get_current_tool_status(self) -> tuple[bool, str]:
        success, response = await asyncio.to_thread(self.arduino_service.send_command, "TOOL", ["currentTool:"])
        if success and response.startswith("currentTool:"):
            try:
                tool_number_str = response.split(":")[1].strip()
                self._current_tool_mode = int(tool_number_str)
            except (IndexError, ValueError):
                self._current_tool_mode = None
                return False, "Failed to parse tool status response."
        return success, response

    async def firing(self, data: dict):

        if data.get("active") is True:
            await self.fire_tool(value=255)

        else:
            await self.tool_off()

