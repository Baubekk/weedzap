from fastapi import FastAPI


class FastAPIWrapper:
    def __init__(self, fastapi):
        self.__fastapi = fastapi
        super().__init__()

    def get_fastapi(self) -> FastAPI:
        return self.__fastapi