from ..target.ATarget import ATarget
from ..SpectralQty import SpectralQty
import astropy.units as u
from astropy.io import ascii
import re


class FileTarget(ATarget):
    """
    A class to create a target from a file containing the spectral flux densities
    """

    def __init__(self, file: str):
        """
        Initialize a new target from a file containing the spectral flux density values

        Parameters
        ----------
        file : str
            The file to read the spectral flux density values from. The file needs to provide two columns: wavelength
            and the corresponding spectral flux density. The format of the file will be guessed by
            `astropy.io.ascii.read(). If the file doesn't provide units via astropy's enhanced CSV format, the units will
            be read from the column headers or otherwise assumed to be *nm* and *W / m^2 / nm*.
        """
        # Create spectral quantity from file
        sfd = SpectralQty.fromFile(file, u.nm, u.W / (u.m ** 2 * u.nm))
        # Initialize the super class
        super().__init__(sfd)
