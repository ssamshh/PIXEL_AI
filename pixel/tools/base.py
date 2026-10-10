from abc import ABC, abstractmethod
class PixelTool(ABC):
    name="tool"; description="PIXEL tool"
    @abstractmethod
    def run(self, **kwargs): ...
