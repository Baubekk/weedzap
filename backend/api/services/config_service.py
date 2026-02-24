import json
import os
from enum import Enum

from ..internal.ac_framework import component, inject
from .arduino_service import ArduinoService



@component
class ConfigService:
    CONFIG_FILE = "../backend/api/config.json"
    DEFAULT_CONFIG = {
        "steps_x": 9.52,
        "steps_y": 202.45,
        "steps_z": 206.0,
        "x_max_l": 730.0,
        "y_max_l": 390.0,
        "z_max_l": 188.0,
        "h_spd_x": 600.0,
        "h_spd_y": 900.0,
        "h_spd_z": 600.0,
        "homing_speed_slow": 200.0,
        "max_speed": 1500.0,
        "accel": 800.0,
        "LED_PIN_STATE": 0,

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
        self.arduino_service.send(f"SET MS {self.get_max_speed()}")
        self.arduino_service.send(f"SET SX {self.get_steps_x()}")
        self.arduino_service.send(f"SET SY {self.get_steps_y()}")
        self.arduino_service.send(f"SET SZ {self.get_steps_z()}")
        self.arduino_service.send(f"SET HX {self.get_h_spd_x()}")
        self.arduino_service.send(f"SET HY {self.get_h_spd_y()}")
        self.arduino_service.send(f"SET HZ {self.get_h_spd_z()}")
        self.arduino_service.send(f"SET HS {self.get_homing_speed_slow()}")
        self.arduino_service.send(f"SET LED {self.get_led_state()}")

    def _set(self, key, value):
        self.__config[key] = value
        self.save_config() # Save config after any change

    def _get(self, key):
        return self.__config.get(key, self.DEFAULT_CONFIG.get(key))
    
    def unsafe_set(self, key, value):
        self._set(key, value)

    def unsafe_get(self, key):
        return self._get(key)
    
    def set_max_speed(self, max_speed):
        self._set("max_speed", max_speed)
        self.arduino_service.send(f"SET MS {max_speed}")

    def get_max_speed(self):
        return self._get("max_speed")
    
    def set_accel(self, accel):
        self._set("accel", accel)

    def get_accel(self):
        return self._get("accel")


    def set_steps_x(self, value: float):
        self._set("steps_x", value)
        self.arduino_service.send(f"SET SX {value}")

    def get_steps_x(self):
        return self._get("steps_x")

    def set_steps_y(self, value: float):
        self._set("steps_y", value)
        self.arduino_service.send(f"SET SY {value}")

    def get_steps_y(self):
        return self._get("steps_y")

    def set_steps_z(self, value: float):
        self._set("steps_z", value)
        self.arduino_service.send(f"SET SZ {value}")

    def get_steps_z(self):
        return self._get("steps_z")

    def set_x_max_l(self, value: float):
        self._set("x_max_l", value)

    def get_x_max_l(self):
        return self._get("x_max_l")

    def set_y_max_l(self, value: float):
        self._set("y_max_l", value)

    def get_y_max_l(self):
        return self._get("y_max_l")

    def set_z_max_l(self, value: float):
        self._set("z_max_l", value)

    def get_z_max_l(self):
        return self._get("z_max_l")
    
    def set_h_spd_x(self, value: float):
        self._set("h_spd_x", value)
        self.arduino_service.send(f"SET HX {value}")

    def get_h_spd_x(self):
        return self._get("h_spd_x")
    
    def set_h_spd_y(self, value: float):
        self._set("h_spd_y", value)
        self.arduino_service.send(f"SET HY {value}")

    def get_h_spd_y(self):
        return self._get("h_spd_y")
    
    def set_h_spd_z(self, value: float):
        self._set("h_spd_z", value)
        self.arduino_service.send(f"SET HZ {value}")

    def get_h_spd_z(self):
        return self._get("h_spd_z")

    def set_homing_speed_slow(self, value: float):
        self._set("homing_speed_slow", value)
        self.arduino_service.send(f"SET HS {value}")

    def get_homing_speed_slow(self):
        return self._get("homing_speed_slow")
    
    def set_led_state(self, value: int):
        self._set("LED_PIN_STATE", value)
        self.arduino_service.send(f"SET LED {value}")
    
    def get_led_state(self):
        return self._get("LED_PIN_STATE")

    def get_all_config(self):
        return self.__config
