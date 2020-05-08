from .AOpticalComponent import AOpticalComponent
from ..IRadiant import IRadiant
from ..SpectralQty import SpectralQty
from ..Entry import Entry
import astropy.units as u
from typing import Union


class StrayLight(AOpticalComponent):
    """
    A class to model additional stray light sources e.g. zodiacal light
    """

    def __init__(self, parent: IRadiant, emission: str):
        """
        Initialize a new stray light source

        Parameters
        ----------
        parent : IRadiant
            The parent element from which the electromagnetic radiation is received.
            This element is usually of type Target or StrayLight.
        emission : str
            Path to the file containing the spectral radiance of the stray light source.
            The format of the file will be guessed by `astropy.io.ascii.read()`.
        """
        # Read the emission
        emission_sqty = SpectralQty.fromFile(emission, wl_unit_default=u.nm,
                                             qty_unit_default=u.W / (u.m ** 2 * u.nm * u.sr))
        # Initialize the super class
        super().__init__(parent, 1.0, emission_sqty)

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
        mes = conf.check_file("emission")
        if mes is not None:
            return mes
