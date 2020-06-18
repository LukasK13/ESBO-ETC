from .AOpticalComponent import AOpticalComponent
from ..IRadiant import IRadiant
import astropy.units as u
from astropy.modeling.models import BlackBody
from ..Entry import Entry
from typing import Union


class CosmicBackground(AOpticalComponent):
    """
    This class models the spectral radiance of the cosmic background as black body radiator
    """

    @u.quantity_input(temp=[u.Kelvin, u.Celsius])
    def __init__(self, parent: IRadiant, temp: u.Quantity = 2.725 * u.K):
        """
        Initialize a new black body point source

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received
        temp : Quantity in Kelvin / Celsius
            Temperature of the black body

        Returns
        -------
        """
        # Create black body model with given temperature
        bb = BlackBody(temperature=temp, scale=1 * u.W / (u.m ** 2 * u.nm * u.sr))
        # Initialize super class
        super().__init__(parent, 1.0, lambda wl: bb(wl))

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
        mes = conf.check_quantity("temp", u.K)
        if mes is not None:
            return mes
