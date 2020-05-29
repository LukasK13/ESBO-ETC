from ..lib.helpers import isLambda, readCSV
from ..lib.logger import logger
from scipy.interpolate import interp1d
import astropy.units as u
import math
from typing import Union, Callable
import os
from scipy.integrate import trapz


# noinspection PyUnresolvedReferences
class SpectralQty:
    """
    A class to hold and work with spectral quantities
    """

    def __init__(self, wl: u.Quantity, qty: u.Quantity, fill_value: Union[bool, int, float] = 0):
        """
        Initialize a new spectral quantity

        Parameters
        ----------
        wl : Quantity
            The binned wavelengths
        qty : Quantity
            The quantity values corresponding to the binned wavelengths. If the values are supplied without a unit,
            they are assumed to be dimensionless.
        fill_value : Union[bool, int, float]
            How to treat missing values. True enables extrapolation, False disables extrapolation and the spectrum will
            be truncated. If a numeric value is given, the missing values will be filled with this value.
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
            logger.error("Lengths not matching")
        self._fill_value = fill_value

    @classmethod
    def fromFile(cls, file: str, wl_unit_default: u.Quantity = None, qty_unit_default: u.Quantity = None,
                 fill_value: Union[bool, int, float] = 0) -> "SpectralQty":
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
        fill_value : Union[bool, int, float]
            How to treat missing values. True enables extrapolation, False disables extrapolation and the spectrum will
            be truncated. If a numeric value is given, the missing values will be filled with this value.
        Returns
        -------
        sqty : SpectralQty
            The created spectral quantity.
        """
        # Read the file
        data = readCSV(file, [wl_unit_default, qty_unit_default] if wl_unit_default is not None and
                       qty_unit_default is not None else None)
        return cls(data[data.colnames[0]].quantity, data[data.colnames[1]].quantity, fill_value=fill_value)

    def __str__(self, precision: int = 4) -> str:
        """
        Convert a SpectralQty object to a string representation

        Parameters
        ----------
        precision : int
            Precision of the printed values

        Returns
        -------
        ret : str
            String representation of the object
        """
        wl_str = []
        qty_str = []
        for i in range(len(self.wl)):
            wl_str_temp = "%%.%dg" % precision % self.wl[i].value
            qty_str_temp = "%%.%dg" % precision % self.qty[i].value
            wl_str.append(wl_str_temp.ljust(max(len(wl_str_temp), len(qty_str_temp)), " "))
            qty_str.append(qty_str_temp.ljust(max(len(wl_str_temp), len(qty_str_temp)), " "))
        return "Wavelength: [" + ", ".join(wl_str) + "] " + self.wl.unit.to_string() + os.linesep +\
               "Quantitiy:  [" + ", ".join(qty_str) + "] " + self.qty.unit.to_string()

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
            return SpectralQty(self.wl, self.qty + other(self.wl).value * other(self.wl[0]).unit)
        # Summand is of type SpectralQty
        else:
            if other.wl.unit.is_equivalent(self.wl.unit) and other.qty.unit.is_equivalent(self.qty.unit):
                if len(self.wl) == len(other.wl) and (self.wl == other.wl).all():
                    # Wavelengths are matching, just add the quantities
                    return SpectralQty(self.wl, self.qty + other.qty)
                else:
                    # Wavelengths are not matching, rebinning needed
                    other_rebinned = other.rebin(self.wl)
                    if len(self.wl) == len(other_rebinned.wl) and (self.wl == other_rebinned.wl).all():
                        return SpectralQty(self.wl, self.qty + other_rebinned.qty)
                    else:
                        # Wavelengths are still not matching as extrapolation is disabled, rebin this spectral quantity
                        return SpectralQty(other_rebinned.wl, self.rebin(other_rebinned.wl).qty + other_rebinned.qty)
            else:
                logger.error("Units are not matching for addition.")

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
            return SpectralQty(self.wl, self.qty - other(self.wl).value * other(self.wl[0]).unit)
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
                logger.error("Units are not matching for substraction.")

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
            return SpectralQty(self.wl, self.qty * other(self.wl).value * other(self.wl[0]).unit)
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
                logger.error("Units are not matching for multiplication.")

    __rmul__ = __mul__

    def __truediv__(self, other: Union[int, float, u.Quantity, "SpectralQty", Callable[[u.Quantity], u.Quantity]]) ->\
            "SpectralQty":
        """
        Calculate the quotient with another object

        Parameters
        ----------
        other : Union[int, float, u.Quantity, "SpectralQty", Callable]
            Divisor for this object. If the binning of the object on the right hand side differs
            from the binning of the left object, the object on the right hand side will be rebinned.

        Returns
        -------
        sum : SpectralQty
            The quotient of both objects
        """
        # Factor is of type int, float or Quantity, just multiply
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, u.Quantity):
            return SpectralQty(self.wl, self.qty / other)
        # Factor is of type lambda
        elif isLambda(other):
            return SpectralQty(self.wl, self.qty / other(self.wl).value / other(self.wl[0]).unit)
        # Factor is of type SpectralQty
        else:
            if other.wl.unit.is_equivalent(self.wl.unit):
                # Wavelengths are matching, just multiply the quantities
                if len(self.wl) == len(other.wl) and (self.wl == other.wl).all():
                    return SpectralQty(self.wl, self.qty / other.qty)
                # Wavelengths are not matching, rebinning needed
                else:
                    # Rebin factor
                    other_rebinned = other.rebin(self.wl)
                    if len(self.wl) == len(other_rebinned.wl) and (self.wl == other_rebinned.wl).all():
                        return SpectralQty(self.wl, self.qty / other_rebinned.qty)
                    else:
                        # Wavelengths are still not matching as extrapolation is disabled, rebin this spectral quantity
                        return SpectralQty(other_rebinned.wl, self.rebin(other_rebinned.wl).qty / other_rebinned.qty)
            else:
                logger.error("Units are not matching for division.")

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
            logger.error("Mismatching units for rebinning: " + wl.unit + ", " + self.wl.unit)
        if min(wl) < min(self.wl) or max(wl) > max(self.wl):
            if isinstance(self._fill_value, bool):
                if not self._fill_value:
                    logger.warning("Extrapolation disabled, bandwidth will be reduced.")
                    # Remove new wavelengths where extrapolation would have been necessary
                    wl = [x.value for x in wl if min(self.wl) <= x <= max(self.wl)] * wl.unit
                f = interp1d(self.wl, self.qty.value, fill_value="extrapolate")
            else:
                f = interp1d(self.wl, self.qty.value, fill_value=self._fill_value, bounds_error=False)
        else:
            f = interp1d(self.wl, self.qty.value)
        return SpectralQty(wl, f(wl.to(self.wl.unit)) * self.qty.unit)

    def integrate(self) -> u.Quantity:
        """
        Integrate the spectral quantity over the given spectrum using

        Returns
        -------
        int : Quantity
            The integrated quantity
        """
        return u.Quantity(trapz(self.qty, self.wl))
