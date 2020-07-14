from ..target.ATarget import ATarget
from ..SpectralQty import SpectralQty
import astropy.units as u
from ..Entry import Entry
from typing import Union


class FileTarget(ATarget):
    """
    A class to create a target from a file containing the spectral flux densities
    """

    @u.quantity_input(wl_bins="length")
    def __init__(self, file: str, wl_bins: u.Quantity):
        """
        Initialize a new target from a file containing the spectral flux density values

        Parameters
        ----------
        file : str
            The file to read the spectral flux density values from. The file needs to provide two columns: wavelength
            and the corresponding spectral flux density. The format of the file will be guessed by
            `astropy.io.ascii.read(). If the file doesn't provide units via astropy's enhanced CSV format, the units
            will be read from the column headers or otherwise assumed to be *nm* and *W / m^2 / nm*.
        wl_bins : length-Quantity
            Wavelengths used for binning
        """
        # Create spectral quantity from file
        sfd = SpectralQty.fromFile(file, u.nm, u.W / (u.m ** 2 * u.nm)).rebin(wl_bins)
        # Initialize the super class
        super().__init__(sfd, wl_bins)

    @staticmethod
    def check_config(conf: Entry) -> Union[None, str]:
        """
        Check the configuration for this class

        Parameters
        ----------
        conf : Entry
            The configuration entry to be checked.

        Returns
        -------
        mes : Union[None, str]
            The error message of the check. This will be None if the check was successful.
        """
        mes = conf.check_file("file")
        if mes is not None:
            return mes
