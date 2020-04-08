from abc import ABC, abstractmethod
from .SpectralQty import SpectralQty


class ITransmissive(ABC):
    @abstractmethod
    def calcSignal(self) -> SpectralQty:
        pass

    @abstractmethod
    def calcNoise(self) -> SpectralQty:
        pass
