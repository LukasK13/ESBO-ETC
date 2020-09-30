from .AOpticalComponent import AOpticalComponent
from ..IRadiant import IRadiant
from ..SpectralQty import SpectralQty
from ..Entry import Entry
from ...lib.logger import logger
import astropy.units as u
from astropy.io import ascii
from astropy.modeling.models import BlackBody
from typing import Union


class Atmosphere(AOpticalComponent):
    """
    A class to model the atmosphere including the atmosphere's spectral transmittance and emission.
    """

    def __init__(self, **kwargs):
        """
        Initialize a new atmosphere model

        Parameters
        ----------
        parent : IRadiant
            The parent element of the atmosphere from which the electromagnetic radiation is received.
            This element is usually of type Target or StrayLight.
        transmittance : str
            Path to the file containing the spectral transmittance-coefficients of the atmosphere.
            The format of the file will be guessed by `astropy.io.ascii.read()`.
        emission : str
            Path to the file containing the spectral radiance of the atmosphere.
            The format of the file will be guessed by `astropy.io.ascii.read()`.
        """

        args = dict()
        if "temp" in kwargs:
            args = self._fromATRAN(**kwargs)
        elif "transmittance" in kwargs:
            args = self._fromFiles(**kwargs)
        else:
            logger.error("Wrong parameters for class Atmosphere.")
        super().__init__(parent=args["parent"], transreflectivity=args["transmittance"], noise=args["emission"])

    def _fromFiles(self, parent: IRadiant, transmittance: str, emission: str = None):
        """
        Initialize a new atmosphere model from two files

        Parameters
        ----------
        parent : IRadiant
            The parent element of the atmosphere from which the electromagnetic radiation is received.
            This element is usually of type Target or StrayLight.
        transmittance : str
            Path to the file containing the spectral transmittance-coefficients of the atmosphere.
            The format of the file will be guessed by `astropy.io.ascii.read()`.
        emission : str
            Path to the file containing the spectral radiance of the atmosphere.
            The format of the file will be guessed by `astropy.io.ascii.read()`.
        """
        # Read the transmittance
        transmittance = SpectralQty.fromFile(transmittance, wl_unit_default=u.nm,
                                             qty_unit_default=u.dimensionless_unscaled)
        if emission is None:
            emission = 0
        else:
            emission = SpectralQty.fromFile(emission, wl_unit_default=u.nm,
                                            qty_unit_default=u.W / (u.m ** 2 * u.nm * u.sr))
        return {"parent": parent, "transmittance": transmittance, "emission": emission}

    def _fromATRAN(self, parent: IRadiant, transmittance: str, temp: u.Quantity):
        transmittance = "data_sofia/atmospheric_transmittance.dat"
        # Read the file
        data = ascii.read(transmittance, format=None)
        # Set units
        data["col2"].unit = u.um
        data["col3"].unit = u.dimensionless_unscaled
        # Create spectral quantity
        transmittance = SpectralQty(data["col2"].quantity, data["col3"].quantity)

        # Create black body
        bb = self.__gb_factory(temp)
        # Calculate emission
        emission = SpectralQty(transmittance.wl, bb(transmittance.wl)) * transmittance
        return {"parent": parent, "transmittance": transmittance, "emission": emission}

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
        mes = conf.check_file("transmittance")
        if mes is not None:
            return mes
        if hasattr(conf, "emission"):
            mes = conf.check_file("emission")
            if mes is not None:
                return mes

    @staticmethod
    @u.quantity_input(temp=[u.Kelvin, u.Celsius])
    def __gb_factory(temp: u.Quantity, em: Union[int, float] = 1):
        """
        Factory for a grey body lambda-function.

        Parameters
        ----------
        temp : Quantity in Kelvin / Celsius
            The temperature fo the grey body.
        em : Union[int, float]
            Emissivity of the the grey body

        Returns
        -------
        bb : Callable
            The lambda function for the grey body.
        """
        bb = BlackBody(temperature=temp, scale=em * u.W / (u.m ** 2 * u.nm * u.sr))
        return lambda wl: bb(wl)
