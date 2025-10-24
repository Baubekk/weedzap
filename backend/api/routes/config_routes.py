from fastapi import Body
from pydantic import Field
from backend.api.internal.ac_framework import inject
from backend.api.main import weedzap
from backend.api.services.config_service import ConfigService, LaserState, MovementMode

fastapi = weedzap.get_fastapi()

class Config:
    speed: float = Field(ge=0, le=10)
    movement_mode: MovementMode

@fastapi.get("/config")
async def get_config(config_service: ConfigService = inject(weedzap, ConfigService)):
    return {
        "speed": config_service.get_speed(),
        "movement_mode": config_service.get_movement_mode()
    }

@fastapi.post("/config")
async def set_config(config: Config, config_service: ConfigService = inject(weedzap, ConfigService)):
    config_service.set_speed(config.speed)
    config_service.set_movement_mode(config.movement_mode)

@fastapi.get("/config/speed")
async def get_speed(config_service: ConfigService = inject(weedzap, ConfigService)):
    return {
        "speed": config_service.get_speed()
    }

@fastapi.post("/config/speed")
async def set_speed(speed: float = Body(..., ge=0, le=10000), config_service: ConfigService = inject(weedzap, ConfigService)):
    config_service.set_speed(speed)

@fastapi.get("/config/movement-mode")
async def get_movement_mode(config_service: ConfigService = inject(weedzap, ConfigService)):
    return {
        "movement_mode": config_service.get_movement_mode()
    }

@fastapi.post("/config/movement-mode")
async def set_movement_mode(movement_mode: MovementMode = Body(..., enum=MovementMode), config_service: ConfigService = inject(weedzap, ConfigService)):
    config_service.set_movement_mode(movement_mode)

@fastapi.get("/config/laser")
async def get_laser_config(config_service: ConfigService = inject(weedzap, ConfigService)):
    return {
        "laser_speed": config_service.get_laser_speed(),
        "laser_acceleration": config_service.get_laser_acceleration(),
        "laser_movement_mode": config_service.get_laser_movement_mode()
    }

@fastapi.post("/config/laser")
async def set_laser_config(laser_config: Config, config_service: ConfigService = inject(weedzap, ConfigService)):
    config_service.set_laser_speed(laser_config.speed)
    config_service.set_laser_acceleration(laser_config.acceleration)
    config_service.set_laser_movement_mode(laser_config.movement_mode)

@fastapi.get("/config/laser/movement-mode")
async def get_laser_movement_mode(config_service: ConfigService = inject(weedzap, ConfigService)):
    return {
        "laser_movement_mode": config_service.get_laser_movement_mode()
    }

@fastapi.post("/config/laser/movement-mode")
async def set_laser_movement_mode(laser_movement_mode: MovementMode = Body(..., enum=MovementMode), config_service: ConfigService = inject(weedzap, ConfigService)):
    config_service.set_laser_movement_mode(laser_movement_mode)

@fastapi.get("/config/laser/speed")
async def get_laser_speed(config_service: ConfigService = inject(weedzap, ConfigService)):
    return {
        "laser_speed": config_service.get_laser_speed()
    }

@fastapi.post("/config/laser/speed")
async def set_laser_speed(laser_speed: float = Body(..., ge=0, le=10000), config_service: ConfigService = inject(weedzap, ConfigService)):
    config_service.set_laser_speed(laser_speed)

@fastapi.get("/config/laser/acceleration")
async def get_laser_acceleration(config_service: ConfigService = inject(weedzap, ConfigService)):
    return {
        "laser_acceleration": config_service.get_laser_acceleration()
    }

@fastapi.post("/config/laser/acceleration")
async def set_laser_acceleration(laser_acceleration: float = Body(..., ge=0, le=10000), config_service: ConfigService = inject(weedzap, ConfigService)):
    config_service.set_laser_acceleration(laser_acceleration)

@fastapi.get("/config/laser/state")
async def get_laser_state(config_service: ConfigService = inject(weedzap, ConfigService)):
    return {
        "laser_state": config_service.get_laser_state()
    }

@fastapi.post("/config/laser/state")
async def set_laser_state(laser_state: LaserState = Body(..., enum=LaserState), config_service: ConfigService = inject(weedzap, ConfigService)):
    config_service.set_laser_state(laser_state)