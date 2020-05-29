from .IPSF import IPSF
from ...lib.helpers import rasterizeCircle
from ..sensor.PixelMask import PixelMask
from ...lib.logger import logger
import numpy as np
import astropy.units as u
import re
from typing import Union
from scipy.optimize import bisect
from scipy.signal import fftconvolve
from scipy.interpolate import interp2d


class Zemax(IPSF):
    """
    A class for modelling the PSF from a Zemax output file
    """

    @u.quantity_input(wl="length", d_aperture="length", pixel_size="length")
    def __init__(self, file: str, f_number: float, wl: u.Quantity, d_aperture: u.Quantity, osf: float,
                 pixel_size: u.Quantity):
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
        osf : float
            The oversampling factor to be used for oversampling the PSF with regards to the pixel size.
        pixel_size : Quantity
            The size of a pixel as length-quantity.
        """
        # Store parameters
        self.__f_number = f_number
        self.__wl = wl
        self.__d_aperture = d_aperture
        self.__osf = osf
        self.__pixel_size = pixel_size
        # Read PSF from file
        with open(file, encoding="utf16") as fp:
            self.__psf = np.genfromtxt((x.replace(",", ".") for x in fp), delimiter='\t', skip_header=21)
        # Read header parameters from the file
        with open(file, encoding="utf16") as fp:
            head = [next(fp) for _ in range(21)]
        # Parse shape of the grid and check the read PSF-array
        shape = [int(x) for x in re.findall("[0-9]+", list(filter(re.compile("Image grid size: ").match, head))[0])]
        if shape != list(self.__psf.shape):
            logger.warning("Not all PSF entries read.")
        # Parse and calculate the grid width
        grid_delta = [float(x.replace(",", ".")) for x in
                      re.findall("[0-9]+,*[0-9]*", list(filter(re.compile("Data area is ").match, head))[0])]
        unit = re.findall(".+(?=\\.$)", re.sub("Data area is [0-9]+,*[0-9]* by [0-9]+,*[0-9]* ", "",
                                               list(filter(re.compile("Data area is ").match, head))[0]))[0]
        # noinspection PyArgumentList
        self.__grid_delta = np.array(grid_delta) / np.array(shape) << u.Unit(unit)
        # Parse the center point of the PSF in the grid
        self.__center_point = [int(x) for x in
                               re.findall("[0-9]+", list(filter(re.compile("Center point is: ").match, head))[0])]
        self.__center_point[0] = self.__psf.shape[0] - self.__center_point[0]
        self.__center_point[1] -= 1

        self.__center_point_os = None
        self.__psf_os = None
        self.__psf_osf = None

    # @u.quantity_input(jitter_sigma=u.arcsec)
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
        # Parse the contained energy
        if type(contained_energy) == str:
            try:
                contained_energy = float(contained_energy) / 100.0 * u.dimensionless_unscaled
            except ValueError:
                logger.error("Could not convert encircled energy to float.")
        elif type(contained_energy) in [int, float]:
            contained_energy = contained_energy / 100 * u.dimensionless_unscaled

        center_point, psf, psf_osf = self.__calcPSF(jitter_sigma)

        # Calculate the maximum possible radius for the circle containing the photometric aperture
        r_max = max(np.sqrt(center_point[0] ** 2 + center_point[1] ** 2),
                    np.sqrt((psf.shape[0] - center_point[0]) ** 2 + center_point[1] ** 2),
                    np.sqrt(center_point[0] ** 2 + (psf.shape[1] - center_point[1]) ** 2),
                    np.sqrt((psf.shape[0] - center_point[0]) ** 2 + (psf.shape[1] - center_point[1]) ** 2))
        # Calculate the total contained energy of the PSF
        total = np.sum(psf)
        # Iterate the optimal radius for the contained energy
        r = bisect(lambda r_c: contained_energy.value - np.sum(
            psf * rasterizeCircle(np.zeros((psf.shape[0], psf.shape[0])), r_c, center_point[0],
                                  center_point[1])) / total, 0, r_max, xtol=1e-1) * 2
        # Calculate the reduced observation angle in lambda / d_ap
        # noinspection PyTypeChecker
        reduced_observation_angle = r / psf_osf * self.__grid_delta[0] / (
                self.__f_number * self.__d_aperture) * self.__d_aperture / self.__wl
        return reduced_observation_angle * u.dimensionless_unscaled

    def __calcPSF(self, jitter_sigma: u.Quantity = None):
        """
        Calculate the PSF from the Zemax-file. This includes oversampling the PSF and convolving with the
        jitter-gaussian.

        Parameters
        ----------
        jitter_sigma : Quantity
            Sigma of the telescope's jitter in arcsec.

        Returns
        -------
        center_point : ndarray
            The indices of the PSF's center point on the grid.
        psf : ndarray
            The PSF.
        psf_osf : float
            The oversampling factor of the returned PSF.
        """
        # Calculate the psf for the PSF based on the current resolution of the PSF
        psf_osf = np.ceil(max(self.__grid_delta) / (2 * self.__pixel_size / self.__osf)).value * 2
        if psf_osf == 1.0:
            # No oversampling is necessary
            psf = self.__psf
            center_point = self.__center_point
        else:
            # Oversampling is necessary, oversample the PSF and calculate the new center point.
            f = interp2d(x=np.arange(self.__psf.shape[1]) - self.__center_point[1],
                         y=np.arange(self.__psf.shape[0]) - self.__center_point[0], z=self.__psf,
                         kind='cubic', copy=False, bounds_error=False, fill_value=None)
            center_point = [(x + 0.5) * psf_osf - 0.5 for x in self.__center_point]
            psf = f((np.arange(self.__psf.shape[1] * psf_osf) - center_point[1]) / psf_osf,
                    (np.arange(self.__psf.shape[0] * psf_osf) - center_point[0]) / psf_osf)
        if jitter_sigma is not None:
            # Convert angular jitter to jitter on focal plane
            jitter_sigma_um = (jitter_sigma.to(u.rad) * self.__f_number * self.__d_aperture / u.rad).to(u.um)
            # Jitter is enabled. Calculate the corresponding gaussian bell and convolve it with the PSF
            if min(self.__grid_delta) / psf_osf < 6 * jitter_sigma_um:
                # 3-sigma interval of the gaussian bell is larger than the grid width
                # Calculate the necessary grid length for the 3-sigma interval of the gaussian bell
                jitter_grid_length = np.ceil(6 * jitter_sigma_um / (min(self.__grid_delta) / psf_osf)).value
                # Make sure, the grid size is odd in order to have a defined kernel center
                jitter_grid_length = int(jitter_grid_length if jitter_grid_length % 2 == 1 else jitter_grid_length + 1)

                # Create a meshgrid containing the x and y coordinates of each point within the first quadrant of the
                # gaussian kernel
                xv, yv = np.meshgrid(range(-int((jitter_grid_length - 1) / 2), 1),
                                     range(-int((jitter_grid_length - 1) / 2), 1))
                # Calculate the gaussian kernel in the first quadrant
                kernel = 1 / (2 * np.pi * jitter_sigma_um.value ** 2) * np.exp(
                    -((xv * min(self.__grid_delta.value) / psf_osf) ** 2 +
                      (yv * min(self.__grid_delta.value) / psf_osf) ** 2) / (2 * jitter_sigma_um.value ** 2))
                # Mirror the kernel from the first quadrant to all other quadrants
                kernel = np.concatenate((kernel, np.flip(kernel, axis=1)[:, 1:]), axis=1)
                kernel = np.concatenate((kernel, np.flip(kernel, axis=0)[1:, :]), axis=0)
                # Normalize kernel
                kernel = kernel / np.sum(kernel)
                # Convolve PSF with gaussian kernel
                psf = fftconvolve(np.pad(psf, int((jitter_grid_length - 1) / 2), mode="constant", constant_values=0),
                                  kernel, mode="same")
                # Calculate new center point
                center_point = [x + int((jitter_grid_length - 1) / 2) for x in center_point]
        # Save the values as object attribute
        self.__center_point_os = center_point
        self.__psf_os = psf
        self.__psf_osf = psf_osf
        return center_point, psf, psf_osf

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
        mask_red_os = self._rebin(mask_red, self.__osf).view(PixelMask)
        # Calculate the new PSF-center indices of the reduced mask
        psf_center_ind = [x * self.__osf for x in psf_center_ind]

        # Get PSF values or calculate them if not available
        if self.__psf_os is not None and self.__center_point_os is not None and self.__psf_osf is not None:
            center_point = self.__center_point_os
            psf = self.__psf_os
            psf_osf = self.__psf_osf
        else:
            center_point, psf, psf_osf = self.__calcPSF(jitter_sigma)
        # Calculate the coordinates of each PSF value in microns
        x = (np.arange(psf.shape[1]) - center_point[1]) * self.__grid_delta[1].to(u.um).value / psf_osf
        y = (np.arange(psf.shape[0]) - center_point[0]) * self.__grid_delta[0].to(u.um).value / psf_osf
        # Initialize a two-dimensional cubic interpolation function for the PSF
        psf_interp = interp2d(x=x, y=y, z=psf, kind='cubic', copy=False, bounds_error=False, fill_value=None)
        # Calculate the values of the PSF for all elements of the reduced mask
        res = psf_interp((np.arange(mask_red_os.shape[1]) - psf_center_ind[1]) * mask_red_os.pixel_size.to(u.um).value,
                         (np.arange(mask_red_os.shape[0]) - psf_center_ind[0]) * mask_red_os.pixel_size.to(u.um).value)
        # Bin the oversampled reduced mask to the original resolution and multiply with the reduced mask to select only
        # the relevant values
        res = mask_red * self._rebin(res, 1 / self.__osf)
        # Integrate the reduced mask and divide by the indefinite integral to get relative intensities
        res = res * mask_red_os.pixel_size.to(u.um).value ** 2 / (
                    psf.sum() * (self.__grid_delta[0].to(u.um).value / psf_osf) ** 2)
        # reintegrate the reduced mask into the complete mask
        mask[y_ind.min():(y_ind.max() + 1), x_ind.min():(x_ind.max() + 1)] = res
        return mask
