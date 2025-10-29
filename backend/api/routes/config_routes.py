from fastapi import APIRouter, Body
from pydantic import Field, BaseModel
from ..services.config_service import ConfigService, LaserState, MovementMode
from ..services.laser_service import LaserService
from ..internal.ac_framework import inject

router = APIRouter()

class Config(BaseModel):
    speed: float = Field(ge=0, le=10000)
    movement_mode: MovementMode

@router.get("/config", response_model=Config)
async def get_config(config_service: ConfigService = inject(ConfigService)):
    return Config(speed=config_service.get_speed(), movement_mode=config_service.get_movement_mode())

@router.post("/config")
async def set_config(config: Config, config_service: ConfigService = inject(ConfigService)):
    config_service.set_speed(config.speed)
    config_service.set_movement_mode(config.movement_mode)

@router.get("/config/speed")
async def get_speed(config_service: ConfigService = inject(ConfigService)):
    return {
        "speed": config_service.get_speed()
    }

@router.post("/config/speed")
async def set_speed(speed: float = Body(..., ge=0, le=10000), config_service: ConfigService = inject(ConfigService)):
    config_service.set_speed(speed)

@router.get("/config/movement-mode")
async def get_movement_mode(config_service: ConfigService = inject(ConfigService)):
    return {
        "movement_mode": config_service.get_movement_mode()
    }

@router.post("/config/movement-mode")
async def set_movement_mode(movement_mode: MovementMode = Body(..., enum=MovementMode), config_service: ConfigService = inject(ConfigService)):
    config_service.set_movement_mode(movement_mode)

@router.get("/config/laser")
async def get_laser_config(config_service: ConfigService = inject(ConfigService), laser_service: LaserService = inject(LaserService)):
    return {
        "laser_speed": config_service.get_laser_speed(),
        "laser_acceleration": config_service.get_laser_acceleration(),
        "laser_movement_mode": config_service.get_laser_movement_mode()
    }

@router.post("/config/laser")
async def set_laser_config(laser_config: Config, config_service: ConfigService = inject(ConfigService), laser_service: LaserService = inject(LaserService)):
    config_service.set_laser_speed(laser_config.speed)
    config_service.set_laser_acceleration(laser_config.acceleration)
    config_service.set_laser_movement_mode(laser_config.movement_mode)

@router.get("/config/laser/movement-mode")
async def get_laser_movement_mode(config_service: ConfigService = inject(ConfigService), laser_service: LaserService = inject(LaserService)):
    return {
        "laser_movement_mode": config_service.get_laser_movement_mode()
    }

@router.post("/config/laser/movement-mode")
async def set_laser_movement_mode(laser_movement_mode: MovementMode = Body(..., enum=MovementMode), config_service: ConfigService = inject(ConfigService), laser_service: LaserService = inject(LaserService)):
    config_service.set_laser_movement_mode(laser_movement_mode)

@router.get("/config/laser/speed")
async def get_laser_speed(config_service: ConfigService = inject(ConfigService), laser_service: LaserService = inject(LaserService)):
    return {
        "laser_speed": config_service.get_laser_speed()
    }

@router.post("/config/laser/speed")
async def set_laser_speed(laser_speed: float = Body(..., ge=0, le=10000), config_service: ConfigService = inject(ConfigService), laser_service: LaserService = inject(LaserService)):
    config_service.set_laser_speed(laser_speed)

@router.get("/config/laser/acceleration")
async def get_laser_acceleration(config_service: ConfigService = inject(ConfigService), laser_service: LaserService = inject(LaserService)):
    return {
        "laser_acceleration": config_service.get_laser_acceleration()
    }

@router.post("/config/laser/acceleration")
async def set_laser_acceleration(laser_acceleration: float = Body(..., ge=0, le=10000), config_service: ConfigService = inject(ConfigService), laser_service: LaserService = inject(LaserService)):
    config_service.set_laser_acceleration(laser_acceleration)

@router.get("/config/laser/state")
async def get_laser_state(config_service: ConfigService = inject(ConfigService), laser_service: LaserService = inject(LaserService)):
    return {
        "laser_state": config_service.get_laser_state()
    }

@router.post("/config/laser/state")
async def set_laser_state(laser_state: LaserState = Body(..., enum=LaserState), config_service: ConfigService = inject(ConfigService), laser_service: LaserService = inject(LaserService)):
    config_service.set_laser_state(laser_state)