import os
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from fastapi.responses import FileResponse
from fastapi.routing import APIRoute, APIWebSocketRoute
from fastapi.staticfiles import StaticFiles

from .helper.websocket_middleware import websocket_middleware

from .internal.ac_framework import App
from .internal.fastapi_wrapper import FastAPIWrapper

from fastapi import APIRouter
from .routes.config_routes import router as config_router
from .routes.websocket_routes import router as websocket_router

from .services.arduino_service import ArduinoService
from .services.config_service import ConfigService
from .services.laser_service import LaserService
from .services.camera_service import CameraService
from .services.singleton_websocket_service import WebsocketService
from .services.movement_service import MovementService

from .services.services import arduino_service
from .services.services import config_service
from .services.services import laser_service
from .services.services import camera_service
from .services.services import websocket_service
from .services.services import movement_service

class WeedzapApp(App, FastAPIWrapper):
    def __init__(self, fastapi: FastAPI):
        App.__init__(self)
        FastAPIWrapper.__init__(self, fastapi = fastapi)

fastapi_app = FastAPI()

weedzap = WeedzapApp(fastapi_app)

weedzap.get_context().add_component(arduino_service)
weedzap.get_context().add_component(config_service)
weedzap.get_context().add_component(laser_service)
weedzap.get_context().add_component(camera_service)
weedzap.get_context().add_component(websocket_service)
weedzap.get_context().add_component(movement_service)

app = weedzap.get_fastapi()

def get_weedzap():
    return weedzap

@app.middleware("http")
async def add_weedzap_app_to_request(request: Request, call_next):
    request.app.state.weedzap_app = weedzap
    response = await call_next(request)
    return response

# async def add_weedzap_app_to_websocket(websocket: WebSocket):
#     websocket.app.state.weedzap_app = weedzap

# websocket_middleware(app, add_weedzap_app_to_websocket)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config_router)
app.include_router(websocket_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join("static", "index.html"))