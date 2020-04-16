from .AOpticalComponent import AOpticalComponent
from ..IRadiant import IRadiant
from ..SpectralQty import SpectralQty
import astropy.units as u


class Atmosphere(AOpticalComponent):
    """
    A class to model the atmosphere including the atmosphere's spectral transmittance and emission.
    """

    def __init__(self, parent: IRadiant, transmittance: str, emission: str = None):
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
        # Read the transmittance
        transmittance_sqty = SpectralQty.fromFile(transmittance, wl_unit_default=u.nm,
                                                  qty_unit_default=u.dimensionless_unscaled)
        if emission is None:
            # No emission is given, initialize the super class
            super().__init__(parent, transmittance_sqty)
        else:
            # Read the emission
            emission_sqty = SpectralQty.fromFile(emission, wl_unit_default=u.nm,
                                                 qty_unit_default=u.W / (u.m ** 2 * u.nm * u.sr))
            # Initialize the super class
            super().__init__(parent, transmittance_sqty, emission_sqty)
