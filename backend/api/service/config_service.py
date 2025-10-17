from enum import Enum

from backend.api.internal.ac_framework import component
from backend.api.main import weedzap

class MovementMode(Enum):
    HOLD = "hold"
    STEP = "step"

@component(weedzap)
class ConfigService:
    def __init__(self):
        pass

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