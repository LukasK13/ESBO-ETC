from abc import abstractmethod
from ..ITransmissive import ITransmissive
from ..SpectralQty import SpectralQty


class ATarget(ITransmissive):
    """
    Abstract super class for target models
    """
    @abstractmethod
    def __init__(self, sfd: SpectralQty):
        """
        Initialize a new target

        Parameters
        ----------
        sfd: SpectralQty
            The spectral flux density of the target
        """
        self._sfd = sfd

    @abstractmethod
    def calcNoise(self) -> SpectralQty:
        """
        Calculate the spectral radiance of the target's noise

        Returns
        -------
        noise : SpectralQty
            The spectral radiance of the target's noise
        """
        return SpectralQty(self.sfd.wl, [0] * len(self.sfd.wl))

    def calcSignal(self) -> SpectralQty:
        """
        Calculate the spectral flux density of the target's signal

        Returns
        -------
        signal : SpectralQty
            The spectral flux density of the target's signal
        """
        return self.sfd

