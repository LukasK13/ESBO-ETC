from typing import Union
import numpy as np
from astropy import units as u
from .IPSF import IPSF
from ..sensor.PixelMask import PixelMask
from scipy.optimize import newton, fmin, bisect
from scipy.special import j0, j1
from scipy.signal import fftconvolve
from scipy.integrate import quad
from scipy.interpolate import interp1d


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
        self.__psf_jitter = None

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
                if not np.isclose(obstruction, 0.0):
                    # Use obstructed airy disk
                    reduced_observation_angle = newton(lambda y: self.airy(np.pi * y, np.sqrt(obstruction)) - 0.5,
                                                       reduced_observation_angle / 2) * 2
                    contained_energy = "fwhm"
            elif contained_energy.lower() == "min":
                # Width of the first minimum of the airy disk
                reduced_observation_angle = 1.22 * 2
                contained_energy = 0.8377 * u.dimensionless_unscaled
                if not np.isclose(obstruction, 0.0):
                    # Use obstructed airy disk
                    reduced_observation_angle = fmin(lambda y: self.airy(np.pi * y, np.sqrt(obstruction)),
                                                     reduced_observation_angle / 2, disp=False)[0] * 2
                    contained_energy = self.airy_int(np.pi * reduced_observation_angle / 2,
                                                     np.sqrt(obstruction)) * u.dimensionless_unscaled
        else:
            # Calculate the width numerically from the integral of the airy disk
            contained_energy = contained_energy / 100 * u.dimensionless_unscaled
            reduced_observation_angle = 2 * bisect(
                lambda y: self.airy_int(np.pi * y, np.sqrt(obstruction)) - contained_energy.value, 0, 100)
        if jitter_sigma is not None and (isinstance(contained_energy, u.Quantity) or isinstance(contained_energy, str)
                                         and contained_energy.lower() == "fwhm"):
            # Convert jitter to reduced observation angle in lambda / d_ap
            jitter_sigma = jitter_sigma.to(u.rad).value * self.__d_aperture / self.__wl.to(u.m)
            # Calculate necessary grid length to accommodate the psf and 3-sigma of the gaussian
            grid_width = (reduced_observation_angle / 2 + 3 * jitter_sigma)
            # Calculate the reduced observation angle of a single detector pixel
            reduced_observation_angle_pixel = (self.__pixel_size / (
                    self.__f_number * self.__d_aperture) * self.__d_aperture / self.__wl).decompose()
            # Calculate the width of each grid element
            dx = reduced_observation_angle_pixel.value / self.__osf
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
            psf = fftconvolve(np.pad(psf, int(n_points), mode="constant", constant_values=0), kernel, mode="same")
            # Reduce the PSF to the positive x-domain
            psf = psf[int((psf.shape[0] - 1) / 2):]
            # Scale the integral of the disturbed PSF equal to the undisturbed PSF
            psf = psf / (np.sum(psf * np.arange(psf.shape[0]) * dx) * dx * 2 * np.pi) * total

            self.__psf_jitter = psf
            if isinstance(contained_energy, str) and contained_energy.lower() == "fwhm":
                reduced_observation_angle = np.argmax(psf < psf[0] / 2) * reduced_observation_angle_pixel.value / \
                                            self.__osf * 2
            else:
                # Calculate the rolling integral of the PSF
                psf_int = np.cumsum(psf * np.arange(psf.shape[0]) * dx) * dx * 2 * np.pi
                # Scale the integral of the disturbed PSF equal to the undisturbed PSF
                psf_int = psf_int / (4 / np.pi) * (1 - obstruction) ** 2
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
        res = np.zeros(x.shape)
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
        if len(res.shape) == 1 and len(res) == 1:
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
        # Calculate the indices of all non-zero elements of the mask
        y_ind, x_ind = np.nonzero(mask)
        # Extract a rectangle containing all non-zero values of the mask
        mask_red = mask[y_ind.min():(y_ind.max() + 1), x_ind.min():(x_ind.max() + 1)]
        # Calculate the new PSF-center indices of the reduced mask
        psf_center_ind = [mask.psf_center_ind[0] - y_ind.min(), mask.psf_center_ind[1] - x_ind.min()]
        # Oversample the reduced mask
        mask_red_os = self.rebin(mask_red, self.__osf).view(PixelMask)
        # Calculate the new PSF-center indices of the reduced mask
        psf_center_ind = [x * self.__osf for x in psf_center_ind]

        reduced_observation_angle_pixel = (mask.pixel_size / (
                self.__f_number * self.__d_aperture) * self.__d_aperture / self.__wl).decompose()
        x_mesh, y_mesh = np.meshgrid(
            (np.arange(mask_red_os.shape[1]) - psf_center_ind[
                1]) * reduced_observation_angle_pixel.value / self.__osf,
            (np.arange(mask_red_os.shape[0]) - psf_center_ind[
                0]) * reduced_observation_angle_pixel.value / self.__osf)
        dist = np.sqrt(x_mesh ** 2 + y_mesh ** 2)
        if jitter_sigma is None:
            res = self.airy(dist * np.pi, np.sqrt(obstruction))
        else:
            if self.__psf_jitter is None:
                self.calcReducedObservationAngle("fwhm", jitter_sigma, obstruction)
            psf_jitter = self.__psf_jitter
            x = np.arange(psf_jitter.shape[0]) * reduced_observation_angle_pixel.value / self.__osf
            psf_interp = interp1d(x=x, y=psf_jitter, kind='cubic', copy=False, bounds_error=False,
                                  fill_value="extrapolate")
            res = psf_interp(dist)

        res = self.rebin(res, 1 / self.__osf)
        res = (mask_red * res).view(np.ndarray)
        # Integrate the reduced mask and divide by the indefinite integral to get relative intensities
        res = res * (reduced_observation_angle_pixel.value / self.__osf) ** 2 / (4 / np.pi) * (1 - obstruction) ** 2
        # reintegrate the reduced mask into the complete mask
        mask[y_ind.min():(y_ind.max() + 1), x_ind.min():(x_ind.max() + 1)] = res
        return mask
