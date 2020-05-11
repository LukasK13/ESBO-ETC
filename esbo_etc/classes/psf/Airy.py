from typing import Union
import numpy as np
from astropy import units as u
from .IPSF import IPSF
from scipy.optimize import newton, fmin, bisect
from scipy.special import j0, j1
from scipy.signal import fftconvolve
from scipy.integrate import quad


class Airy(IPSF):
    """
    A class for modelling the PSF using an airy disk.
    """

    @u.quantity_input(wl="length", d_aperture="length")
    def __init__(self, f_number: float, wl: u.Quantity, d_aperture: u.Quantity, osf: float, pixel_size: u.Quantity):
        """
        Initialize a new PSF from a airy disk.

        Parameters
        ----------
        f_number : float
            The working focal number of the optical system
        wl : Quantity
            The central wavelength which is used for calculating the PSF
        d_aperture : Quantity
            The diameter of the telescope's aperture.
        osf : float
            The oversampling factor to be used for oversampling the PSF with regards to the pixel size.
        pixel_size : Quantity
            The size of a pixel as length-quantity.
        """
        self.__f_number = f_number
        self.__wl = wl
        self.__d_aperture = d_aperture
        self.__osf = osf
        self.__pixel_size = pixel_size

    def calcReducedObservationAngle(self, contained_energy: Union[str, int, float],
                                    jitter_sigma: u.Quantity = None, obstruction: float = 0.0) -> u.Quantity:
        """
        Calculate the reduced observation angle in lambda / d_ap for the given contained energy.

        Parameters
        ----------
        contained_energy : Union[str, int, float]
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
        # Calculate the reduced observation angle in lambda / D for the given encircled energy
        reduced_observation_angle = 0 * u.dimensionless_unscaled
        if type(contained_energy) == str:
            # Encircled energy is of type string
            if contained_energy.lower() == "peak":
                # For the peak value of the PSF, the observation angle becomes zero which leads to one exposed
                # pixel later in the code
                reduced_observation_angle = 0 * u.dimensionless_unscaled
            elif contained_energy.lower() == "fwhm":
                # Width of the FWHM of the airy disk
                reduced_observation_angle = 1.028
                contained_energy = 0.4738 * u.dimensionless_unscaled
                if not np.isclose(obstruction, 0.0):
                    # Use obstructed airy disk
                    reduced_observation_angle = newton(lambda y: self.airy(np.pi * y, np.sqrt(obstruction)) - 0.5,
                                                       reduced_observation_angle / 2) * 2
                    contained_energy = self.airy_int(np.pi * reduced_observation_angle / 2, np.sqrt(obstruction))
            elif contained_energy.lower() == "min":
                # Width of the first minimum of the airy disk
                reduced_observation_angle = 1.22 * 2
                contained_energy = 0.8377 * u.dimensionless_unscaled
                if not np.isclose(obstruction, 0.0):
                    # Use obstructed airy disk
                    reduced_observation_angle = fmin(lambda y: self.airy(np.pi * y, np.sqrt(obstruction)),
                                                     reduced_observation_angle / 2, disp=False)[0] * 2
                    contained_energy = self.airy_int(np.pi * reduced_observation_angle / 2, np.sqrt(obstruction))
        else:
            # Calculate the width numerically from the integral of the airy disk
            contained_energy = contained_energy / 100 * u.dimensionless_unscaled
            reduced_observation_angle = 2 * bisect(
                lambda y: self.airy_int(np.pi * y, np.sqrt(obstruction)) - contained_energy.value, 0, 100)
        if jitter_sigma is not None:
            # Convert jitter to reduced observation angle in lambda / d_ap
            jitter_sigma = jitter_sigma.to(u.rad).value * self.__d_aperture / self.__wl.to(u.m)
            # Calculate necessary grid length to accommodate the psf and 3-sigma of the gaussian
            grid_width = (reduced_observation_angle / 2 + 3 * jitter_sigma)
            # Calculate the reduced observation angle of a single detector pixel
            reduced_observation_angle_pixel = (self.__pixel_size / (
                    self.__f_number * self.__d_aperture) * self.__d_aperture / self.__wl)
            # Calculate the width of each grid element
            dx = reduced_observation_angle_pixel / self.__osf
            # Calculate the necessary number of points on the grid
            n_points = np.ceil(grid_width / dx).value
            # Calculate the corresponding x-coordinates of each grid element
            x = np.arange(1, n_points + 1) * dx
            # Calculate the psf from an airy disk for each element on the grid
            psf = self.airy(np.pi * x, np.sqrt(obstruction))
            # Calculate the integral of the undisturbed airy disk in order to scale the result of the convolution
            total = np.sum(psf * x) * dx * 2 * np.pi
            # Mirror the PSF to the negative x-domain
            psf = np.concatenate((np.flip(psf), np.array([1]), psf))
            # Calculate a gaussian kernel
            kernel = 1 / (2 * np.pi * jitter_sigma ** 2) * np.exp(
                - np.concatenate((np.flip(x), np.array([0]), x)) ** 2 / (2 * jitter_sigma ** 2))
            # Normalize the kernel
            kernel = kernel / np.sum(kernel)
            # Convolve the PSF with gaussian kernel
            psf = fftconvolve(np.pad(psf, int(n_points), mode="constant", constant_values=0),
                              kernel, mode="same")
            # Reduce the PSF to the positive x-domain
            psf = psf[int((psf.shape[0] - 1) / 2):]
            # Calculate the rolling integral of the PSF
            psf_int = np.cumsum(psf * np.arange(psf.shape[0])) * reduced_observation_angle_pixel.value / self.__osf
            # Scale the integral of the disturbed PSF equal to the undisturbed PSF
            psf_int = psf_int / psf_int[-1] * total / (4 / np.pi)
            # Calculate the reduced observation angle
            reduced_observation_angle = np.argmax(
                psf_int > contained_energy) * reduced_observation_angle_pixel.value / self.__osf * 2

        return reduced_observation_angle * u.dimensionless_unscaled

    @staticmethod
    def airy(x: Union[float, np.ndarray], obstruction: float = None):
        """
        Calculate function values of the airy disk

        Parameters
        ----------
        x : Union[float, np.ndarray]
            radial coordinate to calculate the function value for.
        obstruction : float
            The linear central obstruction ratio of the aperture.

        Returns
        -------
        res : Union[float, np.ndarray]
            The function values of the airy disk at the given coordinates
        """
        # Standardize input values
        if not isinstance(x, np.ndarray):
            x = np.array([x])
        # Initialize return values and assign values for the singularity at x=0
        res = np.zeros(len(x))
        res[np.isclose(x, 0.0)] = 1.0
        x_temp = x[np.invert(np.isclose(x, 0.0))]
        if obstruction and not np.isclose(obstruction, 0.0):
            # Use obstructed airy disk
            # See also https://en.wikipedia.org/wiki/Airy_disk#Obscured_Airy_pattern
            res[np.invert(np.isclose(x, 0.0))] = 1 / (1 - obstruction ** 2) ** 2 * (
                    2 * (j1(x_temp) - obstruction * j1(obstruction * x_temp)) / x_temp) ** 2
        else:
            # Use unobstructed airy disk
            # See also https://en.wikipedia.org/wiki/Airy_disk#Mathematical_formulation
            res[np.invert(np.isclose(x, 0.0))] = (2 * j1(x_temp) / x_temp) ** 2
        # Unbox arrays of length 1
        if len(res) == 1:
            res = res[0]
        return res

    @staticmethod
    def airy_int(x: float, obstruction: float = None):
        """
        Calculate the integral of the airy disk from 0 to x.

        Parameters
        ----------
        x : float
            The upper limit for the integration.
        obstruction : float
            The linear central obstruction ratio of the aperture.

        Returns
        -------
        res : float
            The integral of the airy disk.
        """
        if np.isclose(x, 0.0):
            # Short circuit for an integration-range of length 0
            return 0.
        else:
            if obstruction and not np.isclose(obstruction, 0.0):
                # Use integral of obstructed airy disk
                # See also https://en.wikipedia.org/wiki/Airy_disk#Obscured_Airy_pattern
                return 1 / (1 - obstruction ** 2) * (1 - j0(x) ** 2 - j1(x) ** 2 + obstruction ** 2 * (
                        1 - j0(obstruction * x) ** 2 - j1(obstruction * x) ** 2) - 4 * obstruction * quad(
                    lambda y: j1(y) * j1(obstruction * y) / y, 0, x, limit=100, epsrel=1e-6)[0])
            else:
                # Use unobstructed airy disk
                # See also https://en.wikipedia.org/wiki/Airy_disk#Mathematical_formulation
                return 1 - j0(x) ** 2 - j1(x) ** 2

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
