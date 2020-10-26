from .AGriddedPSF import AGriddedPSF
from ...lib.logger import logger
import numpy as np
import astropy.units as u
from astropy.io import fits


class FITS(AGriddedPSF):
    """
    A class for modelling the PSF from a FITS-file
    """

    @u.quantity_input(wl="length", d_aperture="length", pixel_size="length")
    def __init__(self, file: str, f_number: float, wl: u.Quantity, d_aperture: u.Quantity, osf: float,
                 pixel_size: u.Quantity):
        """
        Initialize a new PSF from a FITS-file.

        Parameters
        ----------
        file : str
            Path to the FITS-file. The origin of the coordinate system is in the upper left corner of the matrix
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
        # Open the fits file
        hdul = fits.open(file)

        # Check if a dataset is available
        if len(hdul) < 1:
            logger.error("PSF FITS file must contain a PSF dataset")

        # Extract PSF
        psf = hdul[0].data

        # Extract PSF grid size
        if "XPIXSZ" in hdul[0].header:
            if "YPIXSZ" in hdul[0].header:
                grid_delta = np.array([hdul[0].header["XPIXSZ"], hdul[0].header["YPIXSZ"]]) << u.um
            else:
                grid_delta = np.array([hdul[0].header["XPIXSZ"], hdul[0].header["XPIXSZ"]]) << u.um
        elif "PSFSCALE" in hdul[0].header:
            grid_delta = (2 * f_number * d_aperture * np.tan(hdul[0].header["PSFSCALE"] / 2 * u.arcsec)).to(u.um)
            grid_delta = u.Quantity([grid_delta, grid_delta])
        else:
            grid_delta = u.Quantity([pixel_size, pixel_size])

        # Extract PSF center point
        if "XPSFCTR" in hdul[0].header and "YPSFCTR" in hdul[0].header:
            center_point = [hdul[0].header["XPSFCTR"], hdul[0].header["YPSFCTR"]]
        else:
            center_point = [x / 2 for x in list(psf.shape)]

        # Close the file
        hdul.close()

        super().__init__(psf, f_number, wl, d_aperture, osf, pixel_size, grid_delta, center_point)
