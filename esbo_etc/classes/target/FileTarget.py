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
        # Read the file
        data = ascii.read(file)
        # Check if units are given
        if data[data.colnames[0]].unit is None:
            # Convert values to float
            data[data.colnames[0]] = list(map(float, data[data.colnames[0]]))
            data[data.colnames[1]] = list(map(float, data[data.colnames[1]]))
            # Check if units are given in column headers
            if all([re.search("\\[.+\\]", x) for x in data.colnames]):
                # Extract units from headers and apply them on the columns
                units = [u.Unit(re.findall("(?<=\\[).+(?=\\])", x)[0]) for x in data.colnames]
                data[data.colnames[0]].unit = units[0]
                data[data.colnames[1]].unit = units[1]
            # Use default units
            else:
                data[data.colnames[0]].unit = u.nm
                data[data.colnames[1]].unit = u.W / (u.m ** 2 * u.nm)
        # Create a spectral quantity from the data and initialize the super class
        super().__init__(SpectralQty(data[data.colnames[0]].quantity, data[data.colnames[1]].quantity))
