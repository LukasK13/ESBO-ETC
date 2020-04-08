from esbo_etc.lib.helpers import error
# import numpy as np
# from scipy.integrate import cumtrapz
from scipy.interpolate import interp1d
import astropy.units as u
import math


class SpectralQty:
    """
    A class to hold and work with spectral quantities
    """

    def __init__(self, wl: u.Quantity, qty: u.Quantity):
        """
        Initialize a new spectral quantity

        Parameters
        ----------
        wl : Quantity
            The binned wavelengths
        qty : Quantity
            The quantity values corresponding to the binned wavelengths
        """
        self.wl = wl
        self.qty = qty

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
        return self.wl.unit == other.wl.unit and self.qty.unit == other.qty.unit and \
               all([math.isclose(x, y, rel_tol=1e-5) for x, y in zip(self.wl.value, other.wl.value)]) and \
               all([math.isclose(x, y, rel_tol=1e-5) for x, y in zip(self.qty.value, other.qty.value)])

    def add(self, sqty: "SpectralQty"):
        pass

    def multiply(self, sqty: "SpectralQty"):
        pass

    def rebin(self, wl: u.Quantity):
        """
        Resample the spectral quantity sqty(wl) over the new grid wl, rebinning if necessary, otherwise interpolates.
        Copied from ExoSim (https://github.com/ExoSim/ExoSimPublic).

        Parameters
        ----------
        wl : Quantity
            new binned wavelengths

        Returns
        -------
        """

        if wl.unit != self.wl.unit:
            error("Mismatching units for rebinning: " + wl.unit + ", " + self.wl.unit)

        # idx = np.where(np.logical_and(self.wl > 0.9 * wl.min(), self.wl < 1.1 * wl.max()))[0]
        # wl_old = self.wl[idx]
        # qty_old = self.qty[idx]
        #
        # if np.diff(wl_old).min() < np.diff(wl).min():
        #     # Binning
        #     c = cumtrapz(qty_old, x=wl_old) * qty_old.unit * wl_old.unit
        #     print(c)
        #     xpc = wl_old[1:]
        #
        #     delta = np.gradient(wl)
        #     new_c_1 = np.interp(wl - 0.5 * delta, xpc, c, left=0.0, right=0.0) * c.unit
        #     new_c_2 = np.interp(wl + 0.5 * delta, xpc, c, left=0.0, right=0.0) * c.unit
        #     qty = (new_c_2 - new_c_1) / delta
        # else:
        #     # Interpolation
        #     qty = np.interp(wl, wl_old, qty_old, left=0.0, right=0.0)

        f = interp1d(self.wl, self.qty, fill_value="extrapolate")
        qty = f(wl) * self.qty.unit

        self.wl = wl
        self.qty = qty

        # import matplotlib.pyplot as plt
        # plt.plot(wl_old, qty_old, '-')
        # plt.plot(wl, qty, '.-')
        # plt.show()
        # # check
        # print(np.trapz(qty, wl))
        # idx = np.where(np.logical_and(wl_old >= wl.min(), wl_old <= wl.max()))
        # print(np.trapz(qty_old[idx], wl_old[idx]))
