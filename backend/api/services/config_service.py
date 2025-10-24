from enum import Enum

from backend.api.internal.ac_framework import component
from backend.api.main import weedzap
from backend.api.services.arduino_service import ArduinoService

class MovementMode(Enum):
    HOLD = "hold"
    STEP = "step"

class LaserState(Enum):
    SAFE = "safe"
    ARMED = "armed"

@component(weedzap)
class ConfigService:
    def __init__(self):
        self.get_arduino_service = lambda: weedzap.get(ArduinoService)

    def _set(self, key, value):
        self.__config[key] = value

    def _get(self, key):
        return self.__config[key]
    
    def unsafe_set(self, key, value):
        self._set(key, value)

    def unsafe_get(self, key):
        return self._get(key)
    
    def set_speed(self, speed):
        self.set("speed", speed)

    def get_speed(self):
        return self.get("speed")
    
    def set_movement_mode(self, mode: MovementMode):
        self.set("mode", mode)

    def get_movement_mode(self):
        return self.get("mode")
    
    def set_laser_movement_mode(self, mode: MovementMode):
        self.set("laser_movement_mode", mode)

    def get_laser_movement_mode(self):
        return self.get("laser_movement_mode")
    
    def set_laser_speed(self, speed):
        self.set("laser_speed", speed)

    def get_laser_speed(self):
        return self.get("laser_speed")
    
    def set_laser_acceleration(self, acceleration):
        self.set("laser_acceleration", acceleration)

    def get_laser_acceleration(self):
        return self.get("laser_acceleration")
    
    def set_laser_state(self, state: LaserState):
        self.set("laser_state", state)

    def get_laser_state(self):
        return self.get("laser_state")