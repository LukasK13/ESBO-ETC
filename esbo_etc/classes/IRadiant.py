from abc import ABC, abstractmethod
from .SpectralQty import SpectralQty
from typing import Tuple


class IRadiant(ABC):
    """
    Interface for getting the signal and the background radiation of a emitting, reflecting or transmitting component
    in the beam.
    """
    @abstractmethod
    def calcSignal(self) -> Tuple[SpectralQty, str]:
        """
        Calculate the signal coming from the component

        Returns
        -------
        signal : SpectralQty
            The emitted, reflected or transmitted signal
        size : str
            The size of the target.
        """
        pass

    @abstractmethod
    def calcBackground(self) -> SpectralQty:
        """
        Calculate the background radiation coming from the component

        Returns
        -------
        signal : SpectralQty
            The emitted, reflected or transmitted background radiation
        """
        pass
