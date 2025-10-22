from enum import Enum
from backend.api.internal.ac_framework import component
from backend.api.main import weedzap
from backend.api.services.config_service import ConfigService, MovementMode

class LaserComponent(Enum):
    MOVEMENT = "movement"
    FIRING = "firing"

#fuck the variable naming in this class (i did it myself)
@component(weedzap)
class LaserService:
    def __init__(self):
        self.is_firing = False
        self.get_config_service = lambda: weedzap.get(ConfigService)

    async def handle(self, data: dict):
        component = LaserComponent(data.get("component"))
        if component == LaserComponent.MOVEMENT:
            await self.movement(data.get("data"))
        elif component == LaserComponent.FIRE:
            await self.firing(data.get("data"))
    
    async def movement(self, data: dict):
        movement_mode = MovementMode(data.get("mode"))
        if movement_mode == MovementMode.HOLD:
            if self.get_config_service().get_laser_movement_mode() != MovementMode.HOLD:
                return {"error": "Movement mode is not hold. Change to hold mode first. POST /config/laser/movement-mode with body { \"laser_movement_mode\": \"hold\" }"}
            await self.hold(data.get("data"))
        if movement_mode == MovementMode.STEP:
            if self.get_config_service().get_laser_movement_mode() != MovementMode.STEP:
                return {"error": "Movement mode is not step. Change to step mode first. POST /config/laser/movement-mode with body { \"laser_movement_mode\": \"step\" }"}
            await self.step(data.get("data"))

    async def firing(self, data: dict):
        pass

    async def hold(self, data: dict):
        pass

    async def step(self, data: dict):
        pass