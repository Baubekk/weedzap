from enum import Enum

from ..internal.ac_framework import component, inject
from .arduino_service import ArduinoService

class MovementMode(Enum):
    HOLD = "hold"
    STEP = "step"

class LaserState(Enum):
    SAFE = "safe"
    ARMED = "armed"

@component
class ConfigService:
    def __init__(self, arduino_service: ArduinoService):
        self.__config = {}
        self.set_movement_mode(MovementMode.HOLD)
        self.set_speed(1000)
        self.set_laser_movement_mode(MovementMode.HOLD)
        self.set_laser_speed(1000)
        self.set_laser_acceleration(1000)
        self.set_laser_state(LaserState.SAFE)
        
        self.arduino_service = arduino_service

    def _set(self, key, value):
        self.__config[key] = value

    def _get(self, key):
        return self.__config[key]
    
    def unsafe_set(self, key, value):
        self._set(key, value)

    def unsafe_get(self, key):
        return self._get(key)
    
    def set_speed(self, speed):
        self._set("speed", speed)

    def get_speed(self):
        return self._get("speed")
    
    def set_movement_mode(self, mode: MovementMode):
        self._set("mode", mode)

    def get_movement_mode(self):
        return self._get("mode")
    
    def set_laser_movement_mode(self, mode: MovementMode):
        self._set("laser_movement_mode", mode)

    def get_laser_movement_mode(self):
        return self._get("laser_movement_mode")
    
    def set_laser_speed(self, speed):
        self._set("laser_speed", speed)
        self.arduino_service.send(f"xs {speed}")
        self.arduino_service.send(f"ys {speed}")
        self.arduino_service.send(f"zs {speed}")

    def get_laser_speed(self):
        return self._get("laser_speed")
    
    def set_laser_acceleration(self, acceleration):
        self._set("laser_acceleration", acceleration)
        self.arduino_service.send(f"xa {acceleration}")
        self.arduino_service.send(f"ya {acceleration}")
        self.arduino_service.send(f"za {acceleration}")

    def get_laser_acceleration(self):
        return self._get("laser_acceleration")
    
    def set_laser_state(self, state: LaserState):
        self._set("laser_state", state)

    def get_laser_state(self):
        return self._get("laser_state")
