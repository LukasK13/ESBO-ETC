from .AOpticalComponent import AOpticalComponent
from ..IRadiant import IRadiant
from ..SpectralQty import SpectralQty
import astropy.units as u


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
