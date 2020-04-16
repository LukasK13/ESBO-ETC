from abc import abstractmethod
from ..IRadiant import IRadiant
from ..SpectralQty import SpectralQty
import astropy.units as u
import numpy as np


class ATarget(IRadiant):
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
        self.__sfd = sfd

    def calcNoise(self) -> SpectralQty:
        """
        Calculate the spectral radiance of the target's noise

        Returns
        -------
        noise : SpectralQty
            The spectral radiance of the target's noise
        """
        return SpectralQty(self.__sfd.wl, np.repeat(0, len(self.__sfd.wl)) << u.W / (u.m**2 * u.nm * u.sr))

    def calcSignal(self) -> SpectralQty:
        """
        Calculate the spectral flux density of the target's signal

        Returns
        -------
        signal : SpectralQty
            The spectral flux density of the target's signal
        """
        return self.__sfd
