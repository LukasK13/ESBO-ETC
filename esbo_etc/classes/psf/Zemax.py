import numpy as np
import re
from logging import warning
import astropy.units as u
from scipy.interpolate import RegularGridInterpolator
from scipy.integrate import nquad
from scipy.optimize import bisect
from .IPSF import IPSF


class Zemax(IPSF):
    """
    A class for modelling the PSF from a Zemax output file
    """

    @u.quantity_input(wl="length", d_aperture="length")
    def __init__(self, file: str, f_number: float, wl: u.Quantity, d_aperture: u.Quantity):
        """
        Initialize a new PSF from a Zemax file.

        Parameters
        ----------
        file : str
            Path to the Zemax-file. The origin of the coordinate system is in the lower left corner of the matrix
        f_number : float
            The working focal number of the optical system
        wl : Quantity
            The central wavelength which is used for calculating the PSF
        d_aperture : Quantity
            The diameter of the telescope's aperture.
        """
        # Store parameters
        self.__f_number = f_number
        self.__wl = wl
        self.__d_aperture = d_aperture
        # Read PSF from file
        with open(file, encoding="utf16") as fp:
            self.__psf = np.genfromtxt((x.replace(",", ".") for x in fp), delimiter='\t', skip_header=21)
        # Read header parameters from the file
        with open(file, encoding="utf16") as fp:
            head = [next(fp) for _ in range(21)]
        # Parse shape of the grid and check the read PSF-array
        shape = [int(x) for x in re.findall("[0-9]+", list(filter(re.compile("Image grid size: ").match, head))[0])]
        if shape != list(self.__psf.shape):
            warning("Not all PSF entries read.")
        # Parse and calculate the grid width
        grid_delta = [float(x.replace(",", ".")) for x in
                     re.findall("[0-9]+,*[0-9]*", list(filter(re.compile("Data area is ").match, head))[0])]
        unit = re.findall(".+(?=\\.$)", re.sub("Data area is [0-9]+,*[0-9]* by [0-9]+,*[0-9]* ", "",
                                               list(filter(re.compile("Data area is ").match, head))[0]))[0]
        self.__grid_delta = np.array(grid_delta) / np.array(shape) << u.Unit(unit)
        # Parse the center point of the PSF in the grid
        self.__center_point = [int(x) for x in
                               re.findall("[0-9]+", list(filter(re.compile("Center point is: ").match, head))[0])]

    def calcReducedObservationAngle(self, contained_energy: float) -> u.Quantity:
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
        # Create an linear interpolation function for the PSF and the corresponding grid coordinates
        x_range = np.arange(-(self.__center_point[0] - 1), self.__psf.shape[0] - self.__center_point[0] + 1)
        y_range = np.arange(-(self.__center_point[1] - 1), self.__psf.shape[1] - self.__center_point[1] + 1)
        interp = RegularGridInterpolator((y_range, x_range), np.flip(self.__psf, axis=0))
        # Calculate the maximum possible radius as the smallest distance from the center of the PSF to the borders of
        # the grid.
        r_max = min(self.__center_point[0] - 1, self.__center_point[1] - 1,
                    self.__psf.shape[0] - self.__center_point[0], self.__psf.shape[1] - self.__center_point[1])
        # Calculate the overall integral of the PSF
        total = np.sum(self.__psf)
        # Find the radius of the circle containing the given percentage of energy. Therefore, the interpolation
        # function is numerically integrated within the radius. The Integration radius is optimized using bisection.
        try:
            r = bisect(lambda r_c: contained_energy -
                       nquad(lambda x, y: interp(np.array([y, x])),
                             [lambda y: [-1 * np.sqrt(r_c ** 2 - y ** 2), np.sqrt(r_c ** 2 - y ** 2)],
                             [-r_c, r_c]], opts={"epsrel": 1e-1})[0] / total, 0, r_max, xtol=0.1)
        except ValueError:
            r = r_max
        # Calculate the reduced observation angle for the radius of the circle. Therefore, first convert the radius in
        # grid elements to plate size, then calculate the corresponding observation angle and reduce it.
        reduced_observation_angle = r * self.__grid_delta[0] / (self.__f_number * self.__d_aperture) * \
            self.__d_aperture / self.__wl
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
