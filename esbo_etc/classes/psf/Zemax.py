from .AGriddedPSF import AGriddedPSF
from ...lib.logger import logger
import numpy as np
import astropy.units as u
import re


class Zemax(AGriddedPSF):
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
        # Read PSF from file
        with open(file, encoding="utf16") as fp:
            psf = np.genfromtxt((x.replace(",", ".") for x in fp), delimiter='\t', skip_header=21)
        # Read header parameters from the file
        with open(file, encoding="utf16") as fp:
            head = [next(fp) for _ in range(21)]
        # Parse shape of the grid and check the read PSF-array
        shape = [int(x) for x in re.findall("[0-9]+", list(filter(re.compile("Image grid size: ").match, head))[0])]
        if shape != list(psf.shape):
            logger.warning("Not all PSF entries read.")
        # Parse and calculate the grid width
        grid_delta = [float(x.replace(",", ".")) for x in
                      re.findall("[0-9]+,*[0-9]*", list(filter(re.compile("Data area is ").match, head))[0])]
        unit = re.findall(".+(?=\\.$)", re.sub("Data area is [0-9]+,*[0-9]* by [0-9]+,*[0-9]* ", "",
                                               list(filter(re.compile("Data area is ").match, head))[0]))[0]
        grid_delta = np.array(grid_delta) / np.array(shape) << u.Unit(unit)
        # Parse the center point of the PSF in the grid
        center_point = [int(x) for x in
                        re.findall("[0-9]+", list(filter(re.compile("Center point is: ").match, head))[0])]
        center_point[0] = psf.shape[0] - center_point[0]
        center_point[1] -= 1

        super().__init__(psf, f_number, wl, d_aperture, osf, pixel_size, grid_delta, center_point)
