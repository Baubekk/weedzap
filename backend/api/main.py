from fastapi import FastAPI
from contextlib import asynccontextmanager

from internal.ac_framework import App
from internal.fastapi_wrapper import FastAPIWrapper

class WeedzapApp(App, FastAPIWrapper):
    def __init__(self, fastapi: FastAPI):
        App.__init__(self)
        FastAPIWrapper.__init__(self, fastapi = fastapi)

fastapi_app = FastAPI()

weedzap = WeedzapApp(fastapi_app)

app = weedzap.get_fastapi()