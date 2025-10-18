from fastapi import Depends


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

def component(app: App):
    def wrapper(cls):
        instance = cls()
        app.get_context().add_component(instance)
        cls.get_context = lambda: app.get_context()
        cls.is_component = lambda: True
        cls.get_instance = lambda: instance
        return cls
    return wrapper

def inject(app: App, cls):
    return Depends(lambda: app.get_context().get_component(cls))

