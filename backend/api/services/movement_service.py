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
            return success, response
        finally:
            self._move_lock.release()

    async def home(self):
        success, response = await asyncio.to_thread(self.arduino_service.send_home_command)
        return success, response