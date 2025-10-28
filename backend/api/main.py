from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .internal.ac_framework import App
from .internal.fastapi_wrapper import FastAPIWrapper

from fastapi import APIRouter
from .routes.config_routes import router as config_router
from .routes.websocket_routes import router as websocket_router

from .services.arduino_service import ArduinoService
from .services.config_service import ConfigService
from .services.laser_service import LaserService
from .services.camera_service import CameraService
from .services.websocket_service import WebsocketService
from .services.movement_service import MovementService

class WeedzapApp(App, FastAPIWrapper):
    def __init__(self, fastapi: FastAPI):
        App.__init__(self)
        FastAPIWrapper.__init__(self, fastapi = fastapi)

fastapi_app = FastAPI()

weedzap = WeedzapApp(fastapi_app)

# Register services
weedzap.get_context().add_component(ArduinoService())
weedzap.get_context().add_component(ConfigService())
weedzap.get_context().add_component(LaserService())
weedzap.get_context().add_component(CameraService())
weedzap.get_context().add_component(WebsocketService())
weedzap.get_context().add_component(MovementService())

app = weedzap.get_fastapi()

def get_weedzap():
    return weedzap

@app.middleware("http")
async def add_weedzap_app_to_request(request: Request, call_next):
    request.app.state.weedzap_app = weedzap
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config_router)
app.include_router(websocket_router)