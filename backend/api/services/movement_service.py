from backend.api.internal.ac_framework import component
from backend.api.main import weedzap
from backend.api.services.config_service import ConfigService, MovementMode
from backend.api.services.websocket_service import WebsocketService

@component(weedzap)
class MovementService:
    def __init__(self):
        self.current = None
        self.queued = None
        self.get_config_service = lambda: weedzap.get(ConfigService)

    async def handle(self, data: dict):
        movement_mode = MovementMode(data.get("mode"))
        if movement_mode == MovementMode.HOLD:
            if self.get_config_service().get_movement_mode() != MovementMode.HOLD:
                return {"error": "Movement mode is not hold. Change to hold mode first. POST /config/movement-mode with body { \"movement_mode\": \"hold\" }"}
            await self.hold(data.get("data"))
        elif movement_mode == MovementMode.STEP:
            if self.get_config_service().get_movement_mode() != MovementMode.STEP:
                return {"error": "Movement mode is not step. Change to step mode first. POST /config/movement-mode with body { \"movement_mode\": \"step\" }"}
            await self.step(data.get("data"))

    async def hold(self, data: dict):
        if self.current is not None and data.get("active") is True:
            self.current = data
        else:
            self.current = None

    async def step(self, data: dict):
        if self.current is not None:
            self.queued = data
        else:
            self.current = data