from .AHotOpticalComponent import AHotOpticalComponent
from ..SpectralQty import SpectralQty
from ..ITransmissive import ITransmissive
from astropy import units as u
from typing import Union


class BeamSplitter(AHotOpticalComponent):
    """
    A class to model the optical characteristics of a beam splitter.
    """
    @u.quantity_input(temp=[u.Kelvin, u.Celsius], obstructor_temp=[u.Kelvin, u.Celsius])
    def __init__(self, parent: ITransmissive, transmittance: str,
                 emissivity: Union[int, float, str] = 1, temp: u.Quantity = 0 * u.K,
                 obstruction: float = 0, obstructor_temp: u.Quantity = 0 * u.K, obstructor_emissivity: float = 1):
        """
        Instantiate a new beam splitter model

        Parameters
        ----------
        parent : ITransmissive
            The parent element of the optical component from which the electromagnetic radiation is received.
        transmittance : str
            The spectral transmittance coefficients of the filter.
        emissivity : Union[int, float, str]
            The spectral emissivity coefficient for the optical surface.
        temp: Quantity in Kelvin / Celsius
            Temperature of the optical component
        obstruction : float
            The additional obstruction factor of the optical component. 0 means the component is not obstructed, 1
            denotes a completely obstructed component with therefore no incoming flux. It is important to note, that
            the obstruction factor reflects the obstruction of the optical component additionally to the obstruction
            factors of the prior elements in the beam.
        obstructor_temp : Quantity in Kelvin / Celsius
            Temperature of the obstructing component.
        obstructor_emissivity : float
            Emissivity of the obstructing component.
        """
        self._transmittance = SpectralQty.fromFile(transmittance, u.nm, u.dimensionless_unscaled)
        super().__init__(parent, emissivity, temp, obstruction, obstructor_temp, obstructor_emissivity)

    def propagate(self, sqty: SpectralQty) -> SpectralQty:
        """
        Propagate incoming radiation through the optical component

        Parameters
        ----------
        sqty : SpectralQty
            The incoming radiation

        Returns
        -------
        sqty : SpectralQty
            Manipulated incoming radiation
        """
        return sqty * self._transmittance
