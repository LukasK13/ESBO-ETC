from .AHotOpticalComponent import AHotOpticalComponent
from ..SpectralQty import SpectralQty
from ..IRadiant import IRadiant
from ...lib.logger import logger
from ..Entry import Entry
from astropy import units as u
from typing import Union
import numpy as np


class Filter(AHotOpticalComponent):
    """
    A class to model a filter component and its thermal emission. The model can be created from a file, the name of
    a band or a custom spectral range.
    """
    # Bands from Handbook of Space Astronomy and Astrophysics p. 139
    _band = dict(U=dict(cwl=365 * u.nm, bw=68 * u.nm), B=dict(cwl=440 * u.nm, bw=98 * u.nm),
                 V=dict(cwl=550 * u.nm, bw=89 * u.nm), R=dict(cwl=700 * u.nm, bw=220 * u.nm),
                 I=dict(cwl=900 * u.nm, bw=240 * u.nm), J=dict(cwl=1250 * u.nm, bw=300 * u.nm),
                 H=dict(cwl=1650 * u.nm, bw=400 * u.nm), K=dict(cwl=2200 * u.nm, bw=600 * u.nm),
                 L=dict(cwl=3600 * u.nm, bw=1200 * u.nm), M=dict(cwl=4800 * u.nm, bw=800 * u.nm),
                 N=dict(cwl=10200 * u.nm, bw=2500 * u.nm))

    def __init__(self, **kwargs):
        """
        Instantiate a new filter model

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received.
        transmittance : str
            Path to the file containing the spectral transmittance-coefficients of the filter element.
            The format of the file will be guessed by `astropy.io.ascii.read()`.
        band : str
            The spectral band of the filter. Can be one of [U, B, V, R, I, J, H, K].
        start : length-quantity
            Start wavelength of the pass-band
        end : length-quantity
            End wavelength of the pass-band
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
        args = dict()
        if "band" in kwargs:
            args = self._fromBand(**kwargs)
        elif "transmittance" in kwargs:
            args = self._fromFile(**kwargs)
        elif "start" in kwargs and "end" in kwargs:
            args = self._fromRange(**kwargs)
        else:
            logger.error("Wrong parameters for filter.")
        self._transmittance = args.pop("transmittance")
        super().__init__(**args)

    # @u.quantity_input(temp=[u.Kelvin, u.Celsius], obstructor_temp=[u.Kelvin, u.Celsius])
    def _fromBand(self, parent: IRadiant, band: str, emissivity: Union[str, float] = 1, temp: u.Quantity = 0 * u.K,
                  obstruction: float = 0, obstructor_temp: u.Quantity = 0 * u.K,
                  obstructor_emissivity: float = 1) -> dict:
        """
        Instantiate a new filter model from a spectral band. The filter will be modelled as bandpass filter of
        infinite order and therefore similar to a hat-function.

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received.
        band : str
            The spectral band of the filter. Can be one of [U, B, V, R, I, J, H, K].
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

        Returns
        -------
        args : dict
            The arguments for the class instantiation.
        """
        if band not in self._band.keys():
            logger.error("Band has to be one of '[" + ", ".join(list(self._band.keys())) + "]'")
        return self._fromRange(parent, self._band[band]["cwl"] - self._band[band]["bw"] / 2,
                               self._band[band]["cwl"] + self._band[band]["bw"] / 2, emissivity, temp, obstruction,
                               obstructor_temp, obstructor_emissivity)

    # @u.quantity_input(temp=[u.Kelvin, u.Celsius], obstructor_temp=[u.Kelvin, u.Celsius])
    def _fromFile(self, parent: IRadiant, transmittance: str, emissivity: Union[str, float] = 1,
                  temp: u.Quantity = 0 * u.K, obstruction: float = 0, obstructor_temp: u.Quantity = 0 * u.K,
                  obstructor_emissivity: float = 1) -> dict:
        """
        Instantiate a new filter model from a file containing the spectral transmittance coefficients.

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received.
        transmittance : str
            Path to the file containing the spectral transmittance-coefficients of the filter element.
            The format of the file will be guessed by `astropy.io.ascii.read()`.
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

        Returns
        -------
        args : dict
            The arguments for the class instantiation.
        """
        return {"parent": parent, "transmittance": SpectralQty.fromFile(transmittance, u.nm, u.dimensionless_unscaled),
                "emissivity": emissivity, "temp": temp, "obstruction": obstruction, "obstructor_temp": obstructor_temp,
                "obstructor_emissivity": obstructor_emissivity}

    # @u.quantity_input(start="length", end="length", temp=[u.Kelvin, u.Celsius], obstructor_temp=[u.Kelvin, u.Celsius])
    def _fromRange(self, parent: IRadiant, start: u.Quantity, end: u.Quantity, emissivity: Union[str, float] = 1,
                   temp: u.Quantity = 0 * u.K, obstruction: float = 0, obstructor_temp: u.Quantity = 0 * u.K,
                   obstructor_emissivity: float = 1) -> dict:
        """
        Instantiate a new filter model from a spectral range. The filter will be modelled as bandpass filter of
        infinite order and therefore similar to a hat-function.

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received.
        start : length-quantity
            Start wavelength of the pass-band
        end : length-quantity
            End wavelength of the pass-band
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

        Returns
        -------
        args : dict
            The arguments for the class instantiation.
        """
        return {"parent": parent, "transmittance": self.__filter_factory(start, end),
                "emissivity": emissivity, "temp": temp, "obstruction": obstruction, "obstructor_temp": obstructor_temp,
                "obstructor_emissivity": obstructor_emissivity}

    def _propagate(self, sqty: SpectralQty) -> SpectralQty:
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

    @staticmethod
    @u.quantity_input(start="length", end="length")
    def __filter_factory(start: u.Quantity, end: u.Quantity):
        """
        Create a infinite order bandpass filter

        Parameters
        ----------
        start : length-quantity
            Start wavelength of the pass-band
        end : length-quantity
            End wavelength of the pass-band

        Returns
        -------
        lambda : Callable[[u.Quantity], u.Quantity]
            The filter function
        """
        return lambda wl: np.logical_and(np.greater_equal(wl, start), np.greater_equal(end, wl)).astype(
            int) * u.dimensionless_unscaled

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
        if hasattr(conf, "band"):
            mes = conf.check_selection("band", ["U", "B", "V", "R", "I", "J", "H", "K", "L", "M", "N"])
        elif hasattr(conf, "transmittance"):
            mes = conf.check_file("transmittance")
        elif hasattr(conf, "start") and hasattr(conf, "end"):
            mes = conf.check_quantity("start", u.m)
            if mes is not None:
                return mes
            mes = conf.check_quantity("end", u.m)
        else:
            mes = "Expected one of 'band' / 'transmittance' / 'start' & 'end'."
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
