from .AOpticalComponent import AOpticalComponent
from ..IRadiant import IRadiant
from ..SpectralQty import SpectralQty
from ..Entry import Entry
import astropy.units as u
from astropy.modeling.models import BlackBody
from typing import Union


class Atmosphere(AOpticalComponent):
    """
    A class to model the atmosphere including the atmosphere's spectral transmittance and emission.
    """

    @u.quantity_input(temp=[u.Kelvin, u.Celsius])
    def __init__(self, parent: IRadiant, transmittance: Union[str, float, SpectralQty], emission: str = None,
                 temp: u.Quantity = None):
        """
        Initialize a new atmosphere model

        Parameters
        ----------
        parent : IRadiant
            The parent element of the atmosphere from which the electromagnetic radiation is received.
        transmittance : str, float, SpectralQty
            Path to the file containing the spectral transmittance-coefficients of the atmosphere.
            The format of the file will be guessed by `astropy.io.ascii.read()`.
        emission : str
            Path to the file containing the spectral radiance of the atmosphere.
            The format of the file will be guessed by `astropy.io.ascii.read()`.
        temp : u.Quantity
            The atmospheric temperature for the atmosphere's black body radiation.
        """

        # Read the transmittance
        if isinstance(transmittance, str):
            transmittance_sqty = SpectralQty.fromFile(transmittance, wl_unit_default=u.nm,
                                                      qty_unit_default=u.dimensionless_unscaled)
        else:
            transmittance_sqty = transmittance
        if emission:
            # Read the emission
            emission_sqty = SpectralQty.fromFile(emission, wl_unit_default=u.nm,
                                                 qty_unit_default=u.W / (u.m ** 2 * u.nm * u.sr))
        elif temp is not None:
            # Create black body
            bb = self.__gb_factory(temp)
            # Calculate emission
            emission_sqty = SpectralQty(transmittance_sqty.wl, bb(transmittance_sqty.wl)) * (
                        -1 * transmittance_sqty + 1)
        else:
            emission_sqty = 0

        super().__init__(parent=parent, transreflectivity=transmittance_sqty, noise=emission_sqty)

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
        elif hasattr(conf, "temp"):
            mes = conf.check_quantity("temp", u.K)
            if mes is not None:
                return mes
