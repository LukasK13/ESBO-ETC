import logging
import sys
import traceback
import numpy as np


def error(msg: str, exit_: bool = True):
    """
    Handle errors

    Parameters
    ----------
    msg : str
        Error message to show
    exit_ : bool
        Exit program

    Returns
    -------

    """
    logging.error(msg)
    if exit_:
        traceback.print_stack()
        sys.exit(1)


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


def rasterizeCircle(n: int, radius: float, xc: float, yc: float):
    """
    Map a circle on a rectangular grid.

    Parameters
    ----------
    n : int
        Size of the rectangular grid to map the circle on.
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
    grid = np.zeros((n, n))  # Initialize an empty grid
    xc_pix = int(round(xc))  # X center in pixel coordinates
    x_shift = xc_pix - xc  # X shift of the circle center
    yc_pix = int(round(yc))  # Y center in pixel coordinates
    y_shift = yc_pix - yc  # Y shift of the circle center
    radius_pix = int(np.ceil(radius)) + 1  # Length of the square containing the pixels to be checked
    r2 = radius ** 2  # square of the radius

    grid[yc_pix, xc_pix] = 1  # Set the center pixel by default
    # Create meshgrid for the x and y range of the circle
    dx, dy = np.meshgrid(range(- radius_pix if xc_pix - radius_pix >= 0 else - xc_pix,
                               radius_pix + 1 if n > (xc_pix + radius_pix + 1) else n - xc_pix),
                         range(- radius_pix if yc_pix - radius_pix >= 0 else - yc_pix,
                               radius_pix + 1 if n > (yc_pix + radius_pix + 1) else n - yc_pix))
    dx2 = (dx + x_shift) ** 2  # Square of the x-component of the current pixels radius
    dx_side2 = (dx + x_shift + ((dx < 0) - 0.5)) ** 2  # Square of the x-component of the neighbouring pixels radius
    dy2 = (dy + y_shift) ** 2  # Square of the y-component of the current pixels radius
    dy_side2 = (dy + y_shift + ((dy < 0) - 0.5)) ** 2  # Square of the y-component of the neighbouring pixels radius
    res = np.logical_or(dx_side2 + dy2 <= r2, dx2 + dy_side2 < r2)  # Check if pixel is inside or outside
    grid[(dy.min() + yc_pix):(dy.max() + yc_pix + 1), (dx.min() + xc_pix):(dx.max() + xc_pix + 1)] = res
    # fig, ax = plt.subplots()
    # plt.imshow(grid)
    # circle = plt.Circle((xc, yc), radius, color='r', fill=False)
    # ax.add_artist(circle)
    # plt.show()
    return grid

#
# import numpy as np
# import math
# import matplotlib.pyplot as plt
#
# n = 20  # Grid size, 4 times my visualized output in order to be able to truncate some circles
# radius = 0  # Radius
# xc = 9.5  # X center
# yc = 10.3  # Y center
# grid = np.zeros((n, n))  # Initialize an empty grid
# xc_pix = round(xc)  # X center in pixel coordinates
# x_shift = xc_pix - xc  # X shift of the circle center
# yc_pix = round(yc)  # Y center in pixel coordinates
# y_shift = yc_pix - yc  # Y shift of the circle center
# radius_pix = math.ceil(radius) + 1  # Length of the square containing the pixels to be checked
# r2 = radius ** 2  # square of the radius
#
# grid[xc_pix, yc_pix] = 1  # Set the center pixel by default
# # Iterate over all pixels in x direction
# for dx in np.arange(- radius_pix if xc_pix - radius_pix >= 0 else - xc_pix,
#                     radius_pix + 1 if grid.shape[0] > (xc_pix + radius_pix + 1) else grid.shape[0] - xc_pix):
#     dx2 = (dx + x_shift) ** 2  # Square of the x-component of the current pixels radius
#     # Square of the x-component of the neighbouring pixels radius
#     dx_side2 = (dx + x_shift + (0.5 if dx < 0 else -0.5)) ** 2
#     # Iterate over all pixels in y direction
#     for dy in np.arange(- radius_pix if yc_pix - radius_pix >= 0 else - yc_pix,
#                         radius_pix + 1 if grid.shape[1] > (yc_pix + radius_pix + 1) else grid.shape[1] - yc_pix):
#         dy2 = (dy + y_shift) ** 2  # Square of the y-component of the current pixels radius
#         # Square of the y-component of the neighbouring pixels radius
#         dy_side2 = (dy + y_shift + (0.5 if dy < 0 else -0.5)) ** 2
#         if dx_side2 + dy2 <= r2 or dx2 + dy_side2 < r2:
#             # A centerpoint between the current pixel and the two neighbouring pixels is within
#             # the circle. Mark the current pixel as contained.
#             grid[xc_pix + dx, yc_pix + dy] = 1
#
# fig, ax = plt.subplots()
# plt.imshow(grid.transpose())
# circle = plt.Circle((xc, yc), radius, color='r', fill=False)
# ax.add_artist(circle)
# plt.show()
