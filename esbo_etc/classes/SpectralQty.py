from ..lib.helpers import error, isLambda
from scipy.interpolate import interp1d
import astropy.units as u
import math
from typing import Union, Callable
import logging
from astropy.io import ascii
import re


# noinspection PyUnresolvedReferences
class SpectralQty:
    """
    A class to hold and work with spectral quantities
    """

    def __init__(self, wl: u.Quantity, qty: u.Quantity, extrapolate: bool = False):
        """
        Initialize a new spectral quantity

        Parameters
        ----------
        wl : Quantity
            The binned wavelengths
        qty : Quantity
            The quantity values corresponding to the binned wavelengths. If the values are supplied without a unit,
            they are assumed to be dimensionless.
        extrapolate : bool
            Whether extrapolation should be allowed. If disabled, the spectrum will be truncated and a warning given.
        Returns
        -------
        sqty : SpectralQty
            The created spectral quantity.
        """
        # Check if both lengths are equal
        if len(wl) == len(qty):
            # check if units are given. If not, add a dimensionless unit
            if hasattr(wl, "unit"):
                self.wl = wl
            else:
                self.wl = wl * u.dimensionless_unscaled
            if hasattr(qty, "unit"):
                self.qty = qty
            else:
                self.qty = qty * u.dimensionless_unscaled
        else:
            error("Lengths not matching")
        self._extrapolate = extrapolate

    @classmethod
    def fromFile(cls, file: str, wl_unit_default: u.Quantity = None, qty_unit_default: u.Quantity = None,
                 extrapolate: bool = False) -> "SpectralQty":
        """
        Initialize a new spectral quantity and read the values from a file

        Parameters
        ----------
        file : str
            Path to the file to read the values from. The file needs to provide two columns: wavelength
            and the corresponding spectral quantity. The format of the file will be guessed by
            `astropy.io.ascii.read()`. If the file doesn't provide units via astropy's enhanced CSV format, the units
            will be read from the column headers or otherwise assumed to be *wl_unit_default* and *qty_unit_default*.
        wl_unit_default : Quantity
            Default unit to be used for the wavelength column if no units are provided by the file.
        qty_unit_default : Quantity
            Default unit to be used for the quantity column if no units are provided by the file.
        extrapolate : bool
            Whether extrapolation should be allowed. If disabled, the spectrum will be truncated and a warning given.
        Returns
        -------
        sqty : SpectralQty
            The created spectral quantity.
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
                # noinspection PyArgumentList
                units = [u.Unit(re.findall("(?<=\\[).+(?=\\])", x)[0]) for x in data.colnames]
                data[data.colnames[0]].unit = units[0]
                data[data.colnames[1]].unit = units[1]
            # Use default units
            elif wl_unit_default is not None and qty_unit_default is not None:
                data[data.colnames[0]].unit = wl_unit_default
                data[data.colnames[1]].unit = qty_unit_default
        return cls(data[data.colnames[0]].quantity, data[data.colnames[1]].quantity, extrapolate=extrapolate)

    def __eq__(self, other) -> bool:
        """
        Check if this object is equal to another object

        Parameters
        ----------
        other : SpectralQty
            Object to compare with

        Returns
        -------
        res : bool
            Result of the comparison
        """
        return self.wl.unit.is_equivalent(other.wl.unit) and self.qty.unit.is_equivalent(other.qty.unit) and \
            len(self.wl) == len(other.wl) and len(self.qty) == len(other.qty) and \
            all([math.isclose(x, y, rel_tol=1e-5) for x, y in zip(self.wl.value, other.wl.to(self.wl.unit).value)]) and\
            all([math.isclose(x, y, rel_tol=1e-5) for x, y in zip(self.qty.value, other.qty.to(self.qty.unit).value)])

    def __add__(self, other: Union[int, float, u.Quantity, "SpectralQty", Callable[[u.Quantity], u.Quantity]]) ->\
            "SpectralQty":
        """
        Calculate the sum with another object

        Parameters
        ----------
        other : Union[int, float, u.Quantity, "SpectralQty", Callable]
            Addend to be added to this object. If the binning of the object on the right hand side differs
            from the binning of the left object, the object on the right hand side will be rebinned.

        Returns
        -------
        sum : SpectralQty
            The sum of both objects
        """
        # Summand is of type int or float, use same unit
        if isinstance(other, int) or isinstance(other, float):
            return SpectralQty(self.wl, self.qty + other * self.qty.unit)
        # Summand is of type Quantity
        elif isinstance(other, u.Quantity):
            if other.unit == self.qty.unit:
                return SpectralQty(self.wl, self.qty + other)
            else:
                raise TypeError("Units are not matching for addition.")
        # Summand is of type lambda
        elif isLambda(other):
            return SpectralQty(self.wl, self.qty + [other(wl).value for wl in self.wl] * other(self.wl[0]).unit)
        # Summand is of type SpectralQty
        else:
            if other.wl.unit.is_equivalent(self.wl.unit) and other.qty.unit.is_equivalent(self.qty.unit):
                # Wavelengths are matching, just add the quantities
                if len(self.wl) == len(other.wl) and (self.wl == other.wl).all():
                    return SpectralQty(self.wl, self.qty + other.qty)
                # Wavelengths are not matching, rebinning needed
                else:
                    # Rebin addend
                    other_rebinned = other.rebin(self.wl)
                    if len(self.wl) == len(other_rebinned.wl) and (self.wl == other_rebinned.wl).all():
                        return SpectralQty(self.wl, self.qty + other_rebinned.qty)
                    else:
                        # Wavelengths are still not matching as extrapolation is disabled, rebin this spectral quantity
                        return SpectralQty(other_rebinned.wl, self.rebin(other_rebinned.wl).qty + other_rebinned.qty)
            else:
                error("Units are not matching for addition.")

    __radd__ = __add__

    def __sub__(self, other: Union[int, float, u.Quantity, "SpectralQty", Callable[[u.Quantity], u.Quantity]]) ->\
            "SpectralQty":
        """
        Calculate the difference to another object

        Parameters
        ----------
        other : Union[int, float, u.Quantity, "SpectralQty", Callable]
            Subtrahend to be subtracted from this object. If the binning of the object on the right hand side differs
            from the binning of the left object, the object on the right hand side will be rebinned.

        Returns
        -------
        sum : SpectralQty
            The difference of both objects
        """
        # Subtrahend is of type int or float, use same unit
        if isinstance(other, int) or isinstance(other, float):
            return SpectralQty(self.wl, self.qty - other * self.qty.unit)
        # Subtrahend is of type Quantity
        elif isinstance(other, u.Quantity):
            if other.unit == self.qty.unit:
                return SpectralQty(self.wl, self.qty - other)
            else:
                raise TypeError('Units are not matching for subtraction.')
        # Subtrahend is of type lambda
        elif isLambda(other):
            return SpectralQty(self.wl, self.qty - [other(wl).value for wl in self.wl] * other(self.wl[0]).unit)
        # Subtrahend is of type SpectralQty
        else:
            if other.wl.unit.is_equivalent(self.wl.unit) and other.qty.unit.is_equivalent(self.qty.unit):
                # Wavelengths are matching, just subtract the quantities
                if len(self.wl) == len(other.wl) and (self.wl == other.wl).all():
                    return SpectralQty(self.wl, self.qty - other.qty)
                # Wavelengths are not matching, rebinning needed
                else:
                    # Rebin subtrahend
                    other_rebinned = other.rebin(self.wl)
                    if len(self.wl) == len(other_rebinned.wl) and (self.wl == other_rebinned.wl).all():
                        return SpectralQty(self.wl, self.qty - other_rebinned.qty)
                    else:
                        # Wavelengths are still not matching as extrapolation is disabled, rebin this spectral quantity
                        return SpectralQty(other_rebinned.wl, self.rebin(other_rebinned.wl).qty - other_rebinned.qty)
            else:
                error("Units are not matching for substraction.")

    def __mul__(self, other: Union[int, float, u.Quantity, "SpectralQty", Callable[[u.Quantity], u.Quantity]]) ->\
            "SpectralQty":
        """
        Calculate the product with another object

        Parameters
        ----------
        other : Union[int, float, u.Quantity, "SpectralQty", Callable]
            Factor to be multiplied with this object. If the binning of the object on the right hand side differs
            from the binning of the left object, the object on the right hand side will be rebinned.

        Returns
        -------
        sum : SpectralQty
            The product of both objects
        """
        # Factor is of type int, float or Quantity, just multiply
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, u.Quantity):
            return SpectralQty(self.wl, self.qty * other)
        # Factor is of type lambda
        elif isLambda(other):
            return SpectralQty(self.wl, self.qty * [other(wl).value for wl in self.wl] * other(self.wl[0]).unit)
        # Factor is of type SpectralQty
        else:
            if other.wl.unit.is_equivalent(self.wl.unit):
                # Wavelengths are matching, just multiply the quantities
                if len(self.wl) == len(other.wl) and (self.wl == other.wl).all():
                    return SpectralQty(self.wl, self.qty * other.qty)
                # Wavelengths are not matching, rebinning needed
                else:
                    # Rebin factor
                    other_rebinned = other.rebin(self.wl)
                    if len(self.wl) == len(other_rebinned.wl) and (self.wl == other_rebinned.wl).all():
                        return SpectralQty(self.wl, self.qty * other_rebinned.qty)
                    else:
                        # Wavelengths are still not matching as extrapolation is disabled, rebin this spectral quantity
                        return SpectralQty(other_rebinned.wl, self.rebin(other_rebinned.wl).qty * other_rebinned.qty)
            else:
                error("Units are not matching for multiplication.")

    __rmul__ = __mul__

    def rebin(self, wl: u.Quantity) -> "SpectralQty":
        """
        Resample the spectral quantity sqty(wl) over the new grid wl, rebinning if necessary, otherwise interpolates.
        Copied from ExoSim (https://github.com/ExoSim/ExoSimPublic).

        Parameters
        ----------
        wl : Quantity
            new binned wavelengths

        Returns
        -------
        sqty : SpectralQty
            The rebinned spectral quantity
        """

        if not wl.unit.is_equivalent(self.wl.unit):
            error("Mismatching units for rebinning: " + wl.unit + ", " + self.wl.unit)
        if not self._extrapolate:
            if min(wl) < min(self.wl) or max(wl) > max(self.wl):
                logging.warning("Extrapolation disabled, bandwidth will be reduced.")
                # Remove new wavelengths where extrapolation would have been necessary
                wl = [x.value for x in wl if min(self.wl) <= x <= max(self.wl)] * wl.unit
        f = interp1d(self.wl, self.qty.value, fill_value="extrapolate")
        return SpectralQty(wl, f(wl.to(self.wl.unit)) * self.qty.unit)
