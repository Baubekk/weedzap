import asyncio
from ..internal.ac_framework import component, inject
from .config_service import ConfigService
from .handler_service import HandlerService
from .arduino_service import ArduinoService
import threading

@component
class MovementService:
    def __init__(self, config_service: ConfigService, arduino_service: ArduinoService):

        self.config_service = config_service
        self.arduino_service = arduino_service
        self._move_lock = threading.Lock()


    async def move(self, x: float, y: float, z: float):
        if not self._move_lock.acquire(blocking=False):
            print("Movement in progress, command ignored.")
            return False, "Movement in progress, command ignored."
        try:
            success, response = await asyncio.to_thread(self.arduino_service.send_move_command, x, y, z)
            if success and response.startswith("POS X:"):
                return True, response
            return False, f"Move command failed: {response}"
        finally:
            self._move_lock.release()

    async def jog(self, dx: float, dy: float, dz: float) -> tuple[bool, str]:
        if not self._move_lock.acquire(blocking=False):
            print("Movement in progress, command ignored.")
            return False, "Movement in progress, command ignored."
        try:
            success, response = await asyncio.to_thread(self.arduino_service.send_jog_command, dx, dy, dz)
            return success, response
        finally:
            self._move_lock.release()

    async def home(self):
        success, response = await asyncio.to_thread(self.arduino_service.send_home_command)
        if success and "STATUS: Home OK" in response:
            return True, "Home command successful."
        return False, f"Home command failed: {response}"

    async def get_current_position(self) -> tuple[bool, str]:
        success, response = await asyncio.to_thread(self.arduino_service.send_pos_command)
        if success and response.startswith("POS X:"):
            return True, response
        return False, f"Failed to get current position: {response}"

    async def get_status(self) -> tuple[bool, str]:
        success, response = await asyncio.to_thread(self.arduino_service.send_status_command)
        return success, response