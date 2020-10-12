import numpy as np
from astropy.io import ascii
from astropy.table import Table
import astropy.units as u
import re


def isLambda(obj: object):
    """
    Check if a object is of type lambda

    Parameters
    ----------
    obj : object
        The object to check.

    Returns
    -------
    res : bool
        Result of the check
    """
    return isinstance(obj, type(lambda: None)) and obj.__name__ == (lambda: None).__name__


def rasterizeCircle(grid: np.ndarray, radius: float, xc: float, yc: float):
    """
    Map a circle on a rectangular grid.

    Parameters
    ----------
    grid : ndarray
        The grid to map the circle onto.
    radius : float
        Radius of the circle to be mapped.
    xc : float
        X-index of the circle's center point. The origin of the coordinate system is in the top left corner.
    yc : float
        Y-index of the circle's center point. The origin of the coordinate system is in the top left corner.

    Returns
    -------
    grid: ndarray
        The grid with the circle mapped onto. Each point contained within the circle is marked as 1.
    """
    xc_pix = int(round(xc))  # X center in pixel coordinates
    x_shift = xc_pix - xc  # X shift of the circle center
    yc_pix = int(round(yc))  # Y center in pixel coordinates
    y_shift = yc_pix - yc  # Y shift of the circle center
    radius_pix = int(np.ceil(radius)) + 1  # Length of the square containing the pixels to be checked
    r2 = radius ** 2  # square of the radius

    # Create meshgrid for the x and y range of the circle
    dx, dy = np.meshgrid(range(- radius_pix if xc_pix >= radius_pix else - xc_pix,
                               radius_pix + 1 if grid.shape[1] > (xc_pix + radius_pix + 1) else grid.shape[1] - xc_pix),
                         range(- radius_pix if yc_pix >= radius_pix else - yc_pix,
                               radius_pix + 1 if grid.shape[0] > (yc_pix + radius_pix + 1) else grid.shape[0] - yc_pix))
    dx2 = (dx + x_shift) ** 2  # Square of the x-component of the current pixels radius
    dx_side2 = (dx + x_shift + ((dx < 0) - 0.5)) ** 2  # Square of the x-component of the neighbouring pixels radius
    dy2 = (dy + y_shift) ** 2  # Square of the y-component of the current pixels radius
    dy_side2 = (dy + y_shift + ((dy < 0) - 0.5)) ** 2  # Square of the y-component of the neighbouring pixels radius
    res = np.logical_or(dx_side2 + dy2 <= r2, dx2 + dy_side2 < r2)  # Check if pixel is inside or outside
    grid[(dy.min() + yc_pix):(dy.max() + yc_pix + 1), (dx.min() + xc_pix):(dx.max() + xc_pix + 1)] = res
    grid[yc_pix, xc_pix] = 1  # Set the center pixel by default
    # fig, ax = plt.subplots()
    # plt.imshow(grid)
    # circle = plt.Circle((xc, yc), radius, color='r', fill=False)
    # ax.add_artist(circle)
    # plt.show()
    return grid


def readCSV(file: str, units: list = None, format_: str = None) -> Table:
    """
    Read a CSV file and parse the units in the header

    Parameters
    ----------
    file : str
        The path to the file to read.
    units : list
        A list of the default units for the columns.
    format_ : str
        The format to be used for reading (see also astropy table formats).

    Returns
    -------
    data : Table
        The read table as astropy Table object.
    """
    # Read the file
    data = ascii.read(file, format=format_)
    # Check if units are given
    if data[data.colnames[0]].unit is None:
        # Convert values to float
        for i in range(len(data.columns)):
            data[data.colnames[i]] = list(map(float, data[data.colnames[i]]))
        # Check if units are given in column headers
        if all([re.search("\\[.*\\]", x) for x in data.colnames]):
            # Extract units from headers and apply them on the columns
            # noinspection PyArgumentList
            units_header = [u.Unit(re.findall("(?<=\\[).*(?=\\])", x)[0]) for x in data.colnames]
            for i in range(len(data.columns)):
                data[data.colnames[i]].unit = units_header[i]
            if units is not None and len(units) == len(data.columns):
                for i in range(len(data.columns)):
                    if data[data.colnames[i]].unit.is_equivalent(u.Hz) and units[i].is_equivalent(u.m):
                        data[data.colnames[i]] = data[data.colnames[i]].to(units[i], equivalencies=u.spectral())
                    else:
                        try:
                            data[data.colnames[i]] = data[data.colnames[i]].to(units[i])
                        except:
                            data[data.colnames[i]] = data[data.colnames[i]].to(units[i],
                                                                               equivalencies=u.spectral_density(
                                                                                   u.Quantity(data[data.colnames[0]])))
        # Use default units
        elif units is not None and len(units) == len(data.columns):
            for i in range(len(data.columns)):
                data[data.colnames[i]].unit = units[i]
    return data
