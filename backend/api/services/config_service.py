import json
import os
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
    CONFIG_FILE = "../backend/api/config.json"
    DEFAULT_CONFIG = {
        "steps_x": 80.0,
        "steps_y": 80.0,
        "steps_z": 400.0,
        "limit_x": 500.0,
        "limit_y": 500.0,
        "limit_z": 100.0,
        "max_speed": 2000.0,
        "accel": 1000.0,
        "movement_mode": MovementMode.HOLD.value,
        "laser_movement_mode": MovementMode.HOLD.value,
        "laser_state": LaserState.SAFE.value,
        "speed": 1000.0, # This is for general movement, not laser specific
    }

    def __init__(self, arduino_service: ArduinoService):
        self.arduino_service = arduino_service
        self.__config = {}
        self.load_config()

    def load_config(self):
        config_data = {}
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as f:
                try:
                    config_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from {self.CONFIG_FILE}. Using default config.")

        # Ensure all default keys are present
        for key, default_value in self.DEFAULT_CONFIG.items():
            if key not in config_data:
                config_data[key] = default_value

        self.__config = config_data
        self.save_config()
        self._apply_config_to_arduino()

    def save_config(self):
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self.__config, f, indent=4)
    
    def _apply_config_to_arduino(self):
        # Apply initial configuration to Arduino based on loaded/default values
        self.arduino_service.send(f"SET SPEED {self.get_speed()}")
        self.arduino_service.send(f"SET ACCEL {self.get_acceleration()}")
        self.arduino_service.send(f"SET STEPS_X {self.get_steps_x()}")
        self.arduino_service.send(f"SET STEPS_Y {self.get_steps_y()}")
        self.arduino_service.send(f"SET STEPS_Z {self.get_steps_z()}")
        self.arduino_service.send(f"SET LIM_X {self.get_limit_x()}")
        self.arduino_service.send(f"SET LIM_Y {self.get_limit_y()}")
        self.arduino_service.send(f"SET LIM_Z {self.get_limit_z()}")


    def _set(self, key, value):
        self.__config[key] = value
        self.save_config() # Save config after any change

    def _get(self, key):
        return self.__config.get(key, self.DEFAULT_CONFIG.get(key))
    
    def unsafe_set(self, key, value):
        self._set(key, value)

    def unsafe_get(self, key):
        return self._get(key)
    
    def set_speed(self, speed):
        self._set("max_speed", speed) # Renamed "speed" to "max_speed" to align with arduino code
        self.arduino_service.send(f"SET SPEED {speed}")

    def get_speed(self):
        return self._get("max_speed")
    
    def set_acceleration(self, acceleration):
        self._set("accel", acceleration)
        self.arduino_service.send(f"SET ACCEL {acceleration}")

    def get_acceleration(self):
        return self._get("accel")

    def set_movement_mode(self, mode: MovementMode):
        self._set("movement_mode", mode.value)

    def get_movement_mode(self):
        return MovementMode(self._get("movement_mode"))
    
    def set_laser_movement_mode(self, mode: MovementMode):
        self._set("laser_movement_mode", mode.value)

    def get_laser_movement_mode(self):
        return MovementMode(self._get("laser_movement_mode"))
    

    
    
    def set_laser_state(self, state: LaserState):
        self._set("laser_state", state.value)

    def get_laser_state(self):
        return LaserState(self._get("laser_state"))

    def set_steps_x(self, value: int):
        self._set("steps_x", value)
        self.arduino_service.send(f"SET STEPS_X {value}")

    def get_steps_x(self):
        return self._get("steps_x")

    def set_steps_y(self, value: int):
        self._set("steps_y", value)
        self.arduino_service.send(f"SET STEPS_Y {value}")

    def get_steps_y(self):
        return self._get("steps_y")

    def set_steps_z(self, value: int):
        self._set("steps_z", value)
        self.arduino_service.send(f"SET STEPS_Z {value}")

    def get_steps_z(self):
        return self._get("steps_z")

    def set_limit_x(self, value: int):
        self._set("limit_x", value)
        self.arduino_service.send(f"SET LIM_X {value}")

    def get_limit_x(self):
        return self._get("limit_x")

    def set_limit_y(self, value: int):
        self._set("limit_y", value)
        self.arduino_service.send(f"SET LIM_Y {value}")

    def get_limit_y(self):
        return self._get("limit_y")

    def set_limit_z(self, value: int):
        self._set("limit_z", value)
        self.arduino_service.send(f"SET LIM_Z {value}")

    def get_limit_z(self):
        return self._get("limit_z")

    def get_all_config(self):
        return self.__config
