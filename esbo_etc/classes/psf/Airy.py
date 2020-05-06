from typing import Union
import numpy as np
from astropy import units as u
from .IPSF import IPSF
from scipy.optimize import newton
from scipy.special import j0, j1
from scipy.signal import fftconvolve
from ...lib.helpers import error


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
                contained_energy = 0.4738 * u.dimensionless_unscaled
            elif contained_energy.lower() == "min":
                # Width of the first minimum of the airy disk
                reduced_observation_angle = 1.22 * 2
                contained_energy = 0.8377 * u.dimensionless_unscaled
            else:
                # Try to parse the encircled energy to float
                reduced_observation_angle = 0
                try:
                    contained_energy = float(contained_energy) / 100.0 * u.dimensionless_unscaled
                    # Calculate the width numerically from the integral of the airy disk
                    # See also https://en.wikipedia.org/wiki/Airy_disk#Mathematical_formulation
                    reduced_observation_angle = 2 * newton(
                        lambda x: 1 - j0(np.pi * x) ** 2 - j1(np.pi * x) ** 2 - contained_energy, 1, tol=1e-6)

                except ValueError:
                    error("Could not convert encircled energy to float.")
        elif type(contained_energy) == u.Quantity:
            # Calculate the width numerically from the integral of the airy disk
            reduced_observation_angle = 2 * newton(
                lambda x: 1 - j0(np.pi * x) ** 2 - j1(np.pi * x) ** 2 - contained_energy.value, 1, tol=1e-6)
        else:
            # Calculate the width numerically from the integral of the airy disk
            contained_energy = contained_energy * u.dimensionless_unscaled
            reduced_observation_angle = 2 * newton(
                lambda x: 1 - j0(np.pi * x) ** 2 - j1(np.pi * x) ** 2 - contained_energy.value, 1, tol=1e-6)
        if jitter_sigma is not None and type(contained_energy) == u.Quantity:
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
            psf = (2 * j1(np.pi * x) / (np.pi * x))**2
            # Calculate the integral of the undisturbed airy disk in order to scale teh result of the convolution
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
