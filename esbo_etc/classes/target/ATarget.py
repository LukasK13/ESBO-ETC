from abc import abstractmethod
from ..ITransmissive import ITransmissive
from ..SpectralQty import SpectralQty
import astropy.units as u


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

    def calcNoise(self) -> SpectralQty:
        """
        Calculate the spectral radiance of the target's noise

        Returns
        -------
        noise : SpectralQty
            The spectral radiance of the target's noise
        """
        return SpectralQty(self._sfd.wl, [0] * len(self._sfd.wl) << u.W / (u.m**2 * u.nm * u.sr))

    def calcSignal(self) -> SpectralQty:
        """
        Calculate the spectral flux density of the target's signal

        Returns
        -------
        signal : SpectralQty
            The spectral flux density of the target's signal
        """
        return self._sfd

