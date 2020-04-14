from esbo_etc.classes.optical_component.AOpticalComponent import AOpticalComponent
from esbo_etc.classes.ITransmissive import ITransmissive
from esbo_etc.classes.SpectralQty import SpectralQty
from abc import abstractmethod
import astropy.units as u
from esbo_etc.lib.helpers import gb_factory
from typing import Union, Callable


class AHotOpticalComponent(AOpticalComponent):
    """
    Abstract super class for an optical component with thermal emission
    """
    @abstractmethod
    @u.quantity_input(wl_bins='length', temp=[u.Kelvin, u.Celsius])
    def __init__(self, parent: ITransmissive, emissivity: SpectralQty, temp: u.Quantity):
        """
        Initialize a new optical component with thermal emission

        Parameters
        ----------
        parent : ITransmissive
            The parent element of the optical component from which the electromagnetic radiation is received.
        emissivity : SpectralQty
            The spectral emissivity coefficient for the optical surface.
        temp: Quantity in Kelvin / Celsius
            Temperature of the optical component
        """
        # Initialize super class
        super().__init__(parent)
        if temp > 0 * u.K:
            # Create noise from black body model
            if isinstance(emissivity, SpectralQty):
                bb = gb_factory(temp)
                self._noise = SpectralQty(emissivity.wl, bb(emissivity.wl)) * emissivity
            else:
                bb = gb_factory(temp, emissivity)
                self._noise = bb
        else:
            self._noise = 0

    def ownNoise(self) -> Union[SpectralQty, Callable, int, float]:
        """
        Calculate the noise created by the optical component

        Returns
        -------
        noise : Union[SpectralQty, Callable, int, float]
            The noise created by the optical component
        """
        return self._noise
