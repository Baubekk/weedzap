from abc import ABC, abstractmethod

class HandlerService(ABC):
    @abstractmethod
    async def handle(self, data: dict):
        pass