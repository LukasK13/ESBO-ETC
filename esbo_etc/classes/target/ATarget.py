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
    @u.quantity_input(wl_bins="length")
    def __init__(self, sfd: SpectralQty, wl_bins: u.Quantity):
        """
        Initialize a new target

        Parameters
        ----------
        sfd: SpectralQty
            The spectral flux density of the target
        """
        self.__sfd = sfd
        self.__wl_bins = wl_bins

    def calcNoise(self) -> SpectralQty:
        """
        Calculate the spectral radiance of the target's noise

        Returns
        -------
        noise : SpectralQty
            The spectral radiance of the target's noise
        """
        return SpectralQty(self.__wl_bins, np.repeat(0, len(self.__wl_bins)) << u.W / (u.m**2 * u.nm * u.sr))

    def calcSignal(self) -> SpectralQty:
        """
        Calculate the spectral flux density of the target's signal

        Returns
        -------
        signal : SpectralQty
            The spectral flux density of the target's signal
        """
        return self.__sfd
