from abc import ABC, abstractmethod
import astropy.units as u
import numpy as np
from typing import Union


class IPSF(ABC):
    """
    Interface for modelling a PSF
    """
    @abstractmethod
    def calcReducedObservationAngle(self, contained_energy: Union[str, int, float, u.Quantity]) -> u.Quantity:
        """
        Calculate the reduced observation angle in lambda / d_ap for the given contained energy.

        Parameters
        ----------
        contained_energy : Union[str, int, float, u.Quantity]
            The percentage of energy to be contained within a circle with the diameter reduced observation angle.

        Returns
        -------
        reduced_observation_angle: Quantity
            The reduced observation angle in lambda / d_ap
        """
        pass

    @abstractmethod
    def mapToGrid(self, grid: np.ndarray) -> np.ndarray:
        """
        Map the integrated PSF values to a sensor grid.

        Parameters
        ----------
        grid : ndarray
            The grid to map the values to. The values will only be mapped onto entries with the value 1.

        Returns
        -------
        grid : ndarray
            The grid with the mapped values.
        """
        pass
