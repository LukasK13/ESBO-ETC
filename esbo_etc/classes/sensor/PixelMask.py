import astropy.units as u
from logging import warning
from ...lib.helpers import error, rasterizeCircle
import numpy as np


class PixelMask(np.ndarray):
    """
    A class for modelling the pixel exposure mask for a pixel array.
    """

    @u.quantity_input(pixel_geometry=u.pix, pixel_size="length", center_offset=u.pix)
    def __new__(cls, pixel_geometry: u.Quantity, pixel_size: u.Quantity, center_offset: u.Quantity):
        """
        Create a new pixel mask. Each coordinate is now converted to a index representation (y, x).

        Parameters
        ----------
        pixel_geometry : u.Quantity
            The geometry of the pixel array in pixels [x, y]
        pixel_size : length-Quantity
            The edge length of a pixel (assumed to be square).
        center_offset : u.Quantity
            The offset of the PSF-center relative to the center of the detector array as length-quantity with two
            entries: [offset in x-direction, offset in y-direction]
        """
        # Create the ndarray instance of our type, given the usual
        # ndarray input arguments.  This will call the standard
        # ndarray constructor, but return an object of our type.
        # It also triggers a call to PixelMask.__array_finalize__
        obj = super(PixelMask, cls).__new__(cls, (int(pixel_geometry.value[1]), int(pixel_geometry.value[0])),
                                            dtype=float, buffer=None, offset=0, strides=None, order=None)
        obj[:, :] = 0
        # set the new attributes to the values passed
        obj.pixel_geometry = [pixel_geometry[1], pixel_geometry[0]]
        obj.pixel_size = pixel_size
        obj.center_ind = [pixel_geometry[1].value / 2 - 0.5, pixel_geometry[0].value / 2 - 0.5]
        obj.psf_center_ind = [obj.center_ind[0] + center_offset[1].value, obj.center_ind[1] + center_offset[0].value]
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # ``self`` is a new object resulting from
        # ndarray.__new__(PixelMask, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        #
        # We could have got to the ndarray.__new__ call in 3 ways:
        # From an explicit constructor - e.g. PixelMask():
        #    obj is None
        #    (we're in the middle of the InfoArray.__new__
        #    constructor, and self.pixel_geometry will be set when we return to
        #    PixelMask.__new__)
        if obj is None:
            return
        # From view casting - e.g arr.view(PixelMask):
        #    obj is arr
        #    (type(obj) can be PixelMask)
        # From new-from-template - e.g mask[:3]
        #    type(obj) is PixelMask
        #
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for our attributes, because this
        # method sees all creation of default objects - with the
        # PixelMask.__new__ constructor, but also with
        # arr.view(PixelMask).
        self.pixel_geometry = getattr(obj, 'pixel_geometry', None)
        self.pixel_size = getattr(obj, 'pixel_size', None)
        self.center_ind = getattr(obj, 'center_ind', None)
        self.psf_center_ind = getattr(obj, 'psf_center_ind', None)
        # We do not need to return anything

    @u.quantity_input(radius=u.pix, center_offset=u.pix)
    def createPhotometricAperture(self, shape: str, radius: u.Quantity, center_offset: u.Quantity = None):
        """
        Create a photometric aperture on the pixel mask.

        Parameters
        ----------
        shape : str
            Shape of the photometric aperture. This can be either 'circle' or 'square'.
        radius : u.Quantity
            The radius of the photometric aperture in pixels. In case of a square, the radius equals the half of the
            side length.
        center_offset : u.Quantity
            The offset of the photometric aperture's centre with respect to the array's centre in pixels [x ,y]. The
            origin of the coordinate system is in the upper left corner.

        Returns
        -------

        """
        # Calculate the center coordinates
        if center_offset is not None:
            xc = self.pixel_geometry[1] / 2 - 0.5 * u.pix + center_offset[0]
            yc = self.pixel_geometry[0] / 2 - 0.5 * u.pix + center_offset[1]
        else:
            xc = self.psf_center_ind[1] * u.pix
            yc = self.psf_center_ind[0] * u.pix
        if (xc + radius).value > self.pixel_geometry[0].value - 1 or (xc - radius).value < 0 or\
                (yc + radius).value > self.pixel_geometry[1].value - 1 or (yc - radius).value < 0:
            warning("Some parts of the photometric aperture are outside of the array.")
        if shape.lower() == "circle":
            # Rasterize a circle on the grid
            rasterizeCircle(self, radius.value, xc.value, yc.value)
        elif shape.lower() == "square":
            # Rasterize a square on the grid
            # Calculate the left, right, upper and lower bounds of the square
            x_right = int(round((xc + radius - 1e-6 * u.pix).value))
            if x_right > self.pixel_geometry[0].value - 1:
                x_right = self.pixel_geometry[0].value - 1
            x_left = 0 if (xc - radius).value < 0 else int(round((xc - radius + 1e-6 * u.pix).value))
            y_low = int(round((yc + radius - 1e-6 * u.pix).value))
            if y_low > self.pixel_geometry[1].value - 1:
                y_low = self.pixel_geometry[1].value - 1
            y_up = 0 if (yc - radius).value < 0 else int(round((yc - radius + 1e-6 * u.pix).value))
            # Mark the pixels contained in the square with 1
            self[y_up:(y_low + 1), x_left:(x_right + 1)] = 1
        else:
            error("Unknown photometric aperture shape: '" + shape + "'.")
