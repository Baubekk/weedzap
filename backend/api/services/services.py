from ..services.arduino_service import ArduinoService
from ..services.camera_service import CameraService
from ..services.config_service import ConfigService
from ..services.laser_service import LaserService
from ..services.movement_service import MovementService
from ..services.singleton_websocket_service import WebsocketService

arduino_service = ArduinoService()
websocket_service = WebsocketService()
config_service = ConfigService(arduino_service=arduino_service)
laser_service = LaserService(config_service=config_service, arduino_service=arduino_service)
camera_service = CameraService(websocket_service=websocket_service)
movement_service = MovementService(config_service=config_service)

arduino_service.start()