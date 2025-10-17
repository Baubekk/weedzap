class FastAPIWrapper:
    def __init__(self, fastapi):
        self.__fastapi = fastapi
        super().__init__()

    def get_app(self):
        return self.__fastapi