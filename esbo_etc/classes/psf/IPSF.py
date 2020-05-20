from abc import ABC, abstractmethod
import astropy.units as u
from ..sensor.PixelMask import PixelMask
from typing import Union
import numpy as np


class IPSF(ABC):
    """
    Interface for modelling a PSF
    """
    @abstractmethod
    def calcReducedObservationAngle(self, contained_energy: Union[str, int, float, u.Quantity],
                                    jitter_sigma: u.Quantity = None, obstruction: float = 0.0) -> u.Quantity:
        """
        Calculate the reduced observation angle in lambda / d_ap for the given contained energy.

        Parameters
        ----------
        contained_energy : Union[str, int, float, u.Quantity]
            The percentage of energy to be contained within a circle with the diameter reduced observation angle.
        jitter_sigma : Quantity
            Sigma of the telescope's jitter in arcsec
        obstruction : float
            The central obstruction as ratio A_ob / A_ap

        Returns
        -------
        reduced_observation_angle: Quantity
            The reduced observation angle in lambda / d_ap
        """
        pass

    @abstractmethod
    def mapToPixelMask(self, mask: PixelMask, jitter_sigma: u.Quantity = None, obstruction: float = 0.0) -> PixelMask:
        """
        Map the integrated PSF values to a sensor grid.

        Parameters
        ----------
        obstruction
        mask : PixelMask
            The pixel mask to map the values to. The values will only be mapped onto entries with the value 1.
        jitter_sigma : Quantity
            Sigma of the telescope's jitter in arcsec
        obstruction : float
            The central obstruction as ratio A_ob / A_ap

        Returns
        -------
        mask : PixelMask
            The pixel mask with the integrated PSF values mapped onto each pixel.
        """
        pass

    @staticmethod
    def _rebin(arr: np.ndarray, factor: float):
        """
        Rebin a 2D-array by summing or repeating the elements.

        Parameters
        ----------
        arr : ndarray
            Input array.
        factor : float
            Rebinning factor
        Returns
        -------
        rebinned_array : ndarray
            If the factor is smaller than 1, the data is summed,
            if the factor is bigger than 1, array elements are repeated
        See Also
        --------
        resize : Return a new array with the specified factor.
        """
        m, n = arr.shape
        m_new, n_new = int(m * factor), int(n * factor)
        if factor < 1:
            res = arr.reshape((m_new, int(1 / factor), n_new, int(1 / factor))).sum(3).sum(1)
        elif factor > 1:
            res = np.repeat(np.repeat(arr, int(factor), axis=0), int(factor), axis=1)
        else:
            res = arr
        if isinstance(arr, PixelMask):
            res.pixel_size = res.pixel_size / factor
        return res
