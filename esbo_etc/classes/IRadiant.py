from abc import ABC, abstractmethod
from .SpectralQty import SpectralQty


class IRadiant(ABC):
    """
    Interface for getting the signal and the noise of a emitting, reflecting or transmitting component in the beam.
    """
    @abstractmethod
    def calcSignal(self) -> SpectralQty:
        """
        Calculate the signal coming from the component

        Returns
        -------
        signal : SpectralQty
            The emitted, reflected or transmitted signal
        """
        pass

    @abstractmethod
    def calcNoise(self) -> SpectralQty:
        """
        Calculate the noise coming from the component

        Returns
        -------
        signal : SpectralQty
            The emitted, reflected or transmitted noise
        """
        pass
