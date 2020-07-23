from abc import abstractmethod
from ..IRadiant import IRadiant
from ..SpectralQty import SpectralQty
import astropy.units as u
import numpy as np
from ...lib.logger import logger
from typing import Tuple
from ..Entry import Entry


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
        sfd : SpectralQty
            The spectral flux density of the target
        wl_bins : length-Quantity
            The bins to be used for evaluating spectral quantities.
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
        logger.info("Calculating background for class '" + self.__class__.__name__ + "'.")
        background = SpectralQty(self.__wl_bins, np.repeat(0, len(self.__wl_bins)) << u.W / (u.m**2 * u.nm * u.sr))
        logger.debug(background)
        return background

    def calcSignal(self) -> Tuple[SpectralQty, float]:
        """
        Calculate the spectral flux density of the target's signal

        Returns
        -------
        signal : SpectralQty
            The spectral flux density of the target's signal
        obstruction : float
            The obstruction factor as A_ob / A_ap.
        """
        logger.info("Calculating signal for class '" + self.__class__.__name__ + "'.")
        logger.debug(self.__sfd)
        return self.__sfd, 0.0

    @staticmethod
    @abstractmethod
    def check_config(conf: Entry) -> bool:
        """
        Check the configuration for this class

        Parameters
        ----------
        conf : Entry
            The configuration entry to be checked.

        Returns
        -------
        mes : Union[None, str]
            The error message of the check. This will be None if the check was successful.
        """
        pass
