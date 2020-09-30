from .AHotOpticalComponent import AHotOpticalComponent
from ..SpectralQty import SpectralQty
from ..IRadiant import IRadiant
from ..Entry import Entry
from astropy import units as u
from typing import Union


class Lens(AHotOpticalComponent):
    """
    A class to model the optical characteristics of a lens.
    """
    @u.quantity_input(temp=[u.Kelvin, u.Celsius], obstructor_temp=[u.Kelvin, u.Celsius])
    def __init__(self, parent: IRadiant, transmittance: str, emissivity: Union[str, float] = None,
                 temp: u.Quantity = 0 * u.K, obstruction: float = 0, obstructor_temp: u.Quantity = 0 * u.K,
                 obstructor_emissivity: float = 1):
        """
        Instantiate a new lens model

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received.
        transmittance : str
            The spectral transmittance coefficients of the filter.
        emissivity : Union[str, float]
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
        try:
            self._transmittance = float(transmittance) * u.dimensionless_unscaled
        except ValueError:
            self._transmittance = SpectralQty.fromFile(transmittance, u.nm, u.dimensionless_unscaled)
        if emissivity is None:
            emissivity = -1 * self._transmittance + 1.0
        super().__init__(parent, emissivity, temp, obstruction, obstructor_temp, obstructor_emissivity)

    def _propagate(self, rad: SpectralQty) -> SpectralQty:
        """
        Propagate incoming radiation through the optical component

        Parameters
        ----------
        rad : SpectralQty
            The incoming radiation

        Returns
        -------
        rad : SpectralQty
            Manipulated incoming radiation
        """
        return rad * self._transmittance

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
            mes = conf.check_float("transmittance")
            if mes is not None:
                return mes
        if hasattr(conf, "emissivity"):
            mes = conf.check_file("emissivity")
            if mes is not None:
                mes = conf.check_float("emissivity")
                if mes is not None:
                    return mes
        if hasattr(conf, "temp"):
            mes = conf.check_quantity("temp", u.K)
            if mes is not None:
                return mes
        if hasattr(conf, "obstruction"):
            mes = conf.check_float("obstruction")
            if mes is not None:
                return mes
        if hasattr(conf, "obstructor_temp"):
            mes = conf.check_quantity("obstructor_temp", u.K)
            if mes is not None:
                return mes
        if hasattr(conf, "obstructor_emissivity"):
            mes = conf.check_float("obstructor_emissivity")
            if mes is not None:
                return mes
