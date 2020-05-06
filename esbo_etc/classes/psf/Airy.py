from typing import Union
import numpy as np
from astropy import units as u
from .IPSF import IPSF
from scipy.optimize import newton
from scipy.special import j0, j1
from ...lib.helpers import error


class Airy(IPSF):
    """
    A class for modelling the PSF using an airy disk.
    """

    @u.quantity_input(wl="length", d_aperture="length")
    def __init__(self, wl: u.Quantity, d_aperture: u.Quantity):
        self.__wl = wl
        self.__d_aperture = d_aperture

    def calcReducedObservationAngle(self, contained_energy: Union[str, int, float, u.Quantity],
                                    jitter_sigma: u.Quantity = None) -> u.Quantity:
        """
        Calculate the reduced observation angle in lambda / d_ap for the given contained energy.

        Parameters
        ----------
        contained_energy : Union[str, int, float, u.Quantity]
            The percentage of energy to be contained within a circle with the diameter reduced observation angle.
        jitter_sigma : Quantity
            Sigma of the telescope's jitter in arcsec

        Returns
        -------
        reduced_observation_angle: Quantity
            The reduced observation angle in lambda / d_ap
        """
        # Calculate the reduced observation angle in lambda / D for the given encircled energy
        if type(contained_energy) == str:
            # Encircled energy is of type string
            if contained_energy.lower() == "peak":
                # For the peak value of the PSF, the observation angle becomes zero which leads to one exposed
                # pixel later in the code
                reduced_observation_angle = 0
            elif contained_energy.lower() == "fwhm":
                # Width of the FWHM of the airy disk
                reduced_observation_angle = 1.028
            elif contained_energy.lower() == "min":
                # Width of the first minimum of the airy disk
                reduced_observation_angle = 1.22 * 2
            else:
                # Try to parse the encircled energy to float
                reduced_observation_angle = 0
                try:
                    contained_energy = float(contained_energy) / 100.0 * u.dimensionless_unscaled
                    # Calculate the width numerically from the integral of the airy disk
                    # See also https://en.wikipedia.org/wiki/Airy_disk#Mathematical_formulation
                    reduced_observation_angle = 2 * newton(lambda x: 1 - j0(np.pi * x) ** 2 - j1(np.pi * x) ** 2 -
                                                           contained_energy, 1, tol=1e-6)

                except ValueError:
                    error("Could not convert encircled energy to float.")
        else:
            # Calculate the width numerically from the integral of the airy disk
            reduced_observation_angle = 2 * newton(lambda x: 1 - j0(np.pi * x) ** 2 - j1(np.pi * x) ** 2 -
                                                   contained_energy.value, 1, tol=1e-6)
        return reduced_observation_angle * u.dimensionless_unscaled

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
