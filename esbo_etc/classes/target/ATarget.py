from abc import abstractmethod
from ..IRadiant import IRadiant
from ..SpectralQty import SpectralQty
import astropy.units as u
import numpy as np
from logging import info, debug


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

    def calcBackground(self) -> SpectralQty:
        """
        Calculate the spectral radiance of the target's background

        Returns
        -------
        background : SpectralQty
            The spectral radiance of the target's background
        """
        info("Calculating Noise for class '" + self.__class__.__name__ + "'.")
        background = SpectralQty(self.__wl_bins, np.repeat(0, len(self.__wl_bins)) << u.W / (u.m**2 * u.nm * u.sr))
        debug(background)
        return background

    def calcSignal(self) -> SpectralQty:
        """
        Calculate the spectral flux density of the target's signal

        Returns
        -------
        signal : SpectralQty
            The spectral flux density of the target's signal
        """
        info("Calculating Signal for class '" + self.__class__.__name__ + "'.")
        debug(self.__sfd)
        return self.__sfd
