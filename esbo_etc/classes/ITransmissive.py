from abc import ABC, abstractmethod


class ITransmissive(ABC):
    @abstractmethod
    def calcSignal(self):
        pass

    @abstractmethod
    def calcNoise(self):
        pass
