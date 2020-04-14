from esbo_etc.classes.optical_component.AOpticalComponent import AOpticalComponent
from esbo_etc.classes.ITransmissive import ITransmissive
from esbo_etc.classes.SpectralQty import SpectralQty
from abc import abstractmethod
import astropy.units as u
from astropy.modeling.models import BlackBody


class AHotOpticalComponent(AOpticalComponent):
    """
    Abstract super class for an optical component with thermal emission
    """
    @abstractmethod
    @u.quantity_input(wl_bins='length', temp=[u.Kelvin, u.Celsius])
    def __init__(self, parent: ITransmissive, emissivity: SpectralQty, wl_bins: u.Quantity, temp: u.Quantity):
        """
        Initialize a new optical component with thermal emission

        Parameters
        ----------
        parent : ITransmissive
            The parent element of the optical component from which the electromagnetic radiation is received.
        emissivity : SpectralQty
            The spectral emissivity coefficient for the optical surface.
        wl_bins : Quantity
            Wavelengths used for binning
        temp: Quantity in Kelvin / Celsius
            Temperature of the optical component
        """
        # Initialize super class
        super().__init__(parent)
        if temp > 0 * u.K:
            # Create noise from black body model
            bb = BlackBody(temperature=temp, scale=1. * u.W / (u.m ** 2 * u.nm * u.sr))
            self._noise = SpectralQty(wl_bins, bb(wl_bins)) * emissivity
        else:
            self._noise = 0

    def ownNoise(self) -> SpectralQty:
        """
        Calculate the noise created by the optical component

        Returns
        -------
        noise : SpectralQty
            The noise created by the optical component
        """
        return self._noise
