from fastapi import Depends
from fastapi import Request, WebSocket


class ApplicationContext:
    def __init__(self):
        self.__context = {}
        super().__init__()

    def add_component(self, component):
        self.__context[component.__class__] = component
        self.__context[component.__class__.__name__] = component

        return component
    
    def get_component(self, key: type | str):
        return self.__context[key]

class App:
    def __init__(self):
        self.__context = ApplicationContext()

    def get_context(self):
        return self.__context

def component(cls):
    cls.__is_component = lambda: True
    return cls

def inject(cls):
    async def _get_component(request: Request):
        app = (request).app.state.weedzap_app
        return app.get_context().get_component(cls)

    _get_component.__signature__ = None

    return Depends(_get_component)

