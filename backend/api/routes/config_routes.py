from fastapi import APIRouter, Body
from pydantic import Field, BaseModel
from ..services.config_service import ConfigService

from ..internal.ac_framework import inject

router = APIRouter()

@router.get("/config/all")
async def get_all_config(config_service: ConfigService = inject(ConfigService)):
    return config_service.get_all_config()

@router.post("/config/steps-x")
async def set_steps_x(value: float = Body(..., ge=0.0), config_service: ConfigService = inject(ConfigService)):
    config_service.set_steps_x(value)
    return {"status": "success", "steps_x": value}

@router.post("/config/steps-y")
async def set_steps_y(value: float = Body(..., ge=0.0), config_service: ConfigService = inject(ConfigService)):
    config_service.set_steps_y(value)
    return {"status": "success", "steps_y": value}

@router.post("/config/steps-z")
async def set_steps_z(value: float = Body(..., ge=0.0), config_service: ConfigService = inject(ConfigService)):
    config_service.set_steps_z(value)
    return {"status": "success", "steps_z": value}

@router.post("/config/x-max-l")
async def set_x_max_l(value: float = Body(..., ge=0.0), config_service: ConfigService = inject(ConfigService)):
    config_service.set_x_max_l(value)
    return {"status": "success", "x_max_l": value}

@router.post("/config/y-max-l")
async def set_y_max_l(value: float = Body(..., ge=0.0), config_service: ConfigService = inject(ConfigService)):
    config_service.set_y_max_l(value)
    return {"status": "success", "y_max_l": value}

@router.post("/config/z-max-l")
async def set_z_max_l(value: float = Body(..., ge=0.0), config_service: ConfigService = inject(ConfigService)):
    config_service.set_z_max_l(value)
    return {"status": "success", "z_max_l": value}

@router.post("/config/h-spd-x")
async def set_h_spd_x(value: float = Body(..., ge=0.0), config_service: ConfigService = inject(ConfigService)):
    config_service.set_h_spd_x(value)
    return {"status": "success", "h_spd_x": value}

@router.post("/config/h-spd-y")
async def set_h_spd_y(value: float = Body(..., ge=0.0), config_service: ConfigService = inject(ConfigService)):
    config_service.set_h_spd_y(value)
    return {"status": "success", "h_spd_y": value}

@router.post("/config/h-spd-z")
async def set_h_spd_z(value: float = Body(..., ge=0.0), config_service: ConfigService = inject(ConfigService)):
    config_service.set_h_spd_z(value)
    return {"status": "success", "h_spd_z": value}

@router.post("/config/homing-speed-slow")
async def set_homing_speed_slow(value: float = Body(..., ge=0.0), config_service: ConfigService = inject(ConfigService)):
    config_service.set_homing_speed_slow(value)
    return {"status": "success", "homing_speed_slow": value}

@router.post("/config/max-speed")
async def set_max_speed(value: float = Body(..., ge=0.0), config_service: ConfigService = inject(ConfigService)):
    config_service.set_max_speed(value)
    return {"status": "success", "max_speed": value}

@router.post("/config/accel")
async def set_accel(value: float = Body(..., ge=0.0), config_service: ConfigService = inject(ConfigService)):
    config_service.set_accel(value)
    return {"status": "success", "accel": value}

@router.post("/config/led-state")
async def set_led_state(value: int = Body(..., ge=0, le=1), config_service: ConfigService = inject(ConfigService)):
    config_service.set_led_state(value)
    return {"status": "success", "LED_PIN_STATE": value}
