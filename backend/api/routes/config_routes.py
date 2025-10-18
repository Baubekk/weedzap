from fastapi import Body
from pydantic import Field
from backend.api.internal.ac_framework import inject
from backend.api.main import weedzap
from backend.api.services.config_service import ConfigService, MovementMode

fastapi = weedzap.get_fastapi()

class Config:
    speed: float = Field(ge=0, le=10)
    movement_mode: MovementMode

@fastapi.get("/config")
async def get_config():
    return {
        "speed": weedzap.get_config().get_speed(), 
        "movement_mode": weedzap.get_config().get_movement_mode()
    }

@fastapi.post("/config")
async def set_config(config: Config, config_service: ConfigService = inject(weedzap, ConfigService)):
    config_service.set_speed(config.speed)
    config_service.set_movement_mode(config.movement_mode)

@fastapi.get("/config/speed")
async def get_speed():
    return {
        "speed": weedzap.get_config().get_speed()
    }

@fastapi.post("/config/speed")
async def set_speed(speed: float = Body(..., ge=0, le=10), config_service: ConfigService = inject(weedzap, ConfigService)):
    config_service.set_speed(speed)

@fastapi.get("/config/movement_mode")
async def get_movement_mode():
    return {
        "movement_mode": weedzap.get_config().get_movement_mode()
    }

@fastapi.post("/config/movement_mode")
async def set_movement_mode(movement_mode: MovementMode, config_service: ConfigService = inject(weedzap, ConfigService)):
    config_service.set_movement_mode(movement_mode)