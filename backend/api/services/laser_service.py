from enum import Enum
from ..internal.ac_framework import component, inject
from .arduino_service import ArduinoService
from .config_service import ConfigService, LaserState, MovementMode
from .handler_service import HandlerService

class LaserComponent(Enum):
    MOVEMENT = "movement"
    FIRING = "firing"

#fuck the variable naming in this class (i did it myself)
@component
class LaserService(HandlerService):
    def __init__(self, config_service: ConfigService, arduino_service: ArduinoService):
        self.config_service = config_service
        self.arduino_service = arduino_service

    async def handle(self, data: dict):
        component = LaserComponent(data.get("component"))
        if component == LaserComponent.MOVEMENT:
            await self.movement(data.get("data"))
        elif component == LaserComponent.FIRING:
            await self.firing(data.get("data"))
    
    async def movement(self, data: dict):
        movement_mode = MovementMode(data.get("mode"))
        if movement_mode == MovementMode.HOLD:
            if self.config_service.get_laser_movement_mode() != MovementMode.HOLD:
                return {"error": "Movement mode is not hold. Change to hold mode first. POST /config/laser/movement-mode with body { \"laser_movement_mode\": \"hold\" }"}
            await self.hold(data.get("data"))
        if movement_mode == MovementMode.STEP:
            if self.config_service.get_laser_movement_mode() != MovementMode.STEP:
                return {"error": "Movement mode is not step. Change to step mode first. POST /config/laser/movement-mode with body { \"laser_movement_mode\": \"step\" }"}
            await self.step(data.get("data"))

    async def firing(self, data: dict):
        if self.config_service.get_laser_state() != LaserState.ARMED:
            return {"error": "Laser is not armed. Change to armed state first. POST /config/laser/state with body { \"laser_state\": \"armed\" }. When done, POST /config/laser/state with body { \"laser_state\": \"safe\" }"}
        if data.get("active") is True:
            await self.arduino_service.send("l 1")
        else:
            await self.arduino_service.send("l 0")

    async def hold(self, data: dict):
        axis = data.get("axis")
        if axis not in ["x", "y", "z"]:
            return {"error": "Invalid axis"}
        active = data.get("active")

        msg = axis + "h "
        if active is True:
            positive = data.get("positive")
            if positive is True:
                msg += "1"
            else:
                msg += "-1"
        else:
            msg += "0"

        await self.arduino_service.send(msg)
            

    async def step(self, data: dict):
        axis = data.get("axis")
        if axis not in ["x", "y", "z"]:
            return {"error": "Invalid axis"}
        value = data.get("value")
        if not isinstance(value, int):
            return {"error": "Value must be an integer"}

        msg = f"{axis}s {value}"

        await self.arduino_service.send(msg)