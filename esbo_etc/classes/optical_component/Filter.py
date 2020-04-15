from .AHotOpticalComponent import AHotOpticalComponent
from ..SpectralQty import SpectralQty
from ..ITransmissive import ITransmissive
from ...lib.helpers import error
from astropy import units as u
from typing import Union, Callable


class Filter(AHotOpticalComponent):
    """
    A class to model a filter component and its thermal emission. The model can be created from a file, the name of
    a band or a custom spectral range.
    """
    _band_central_wl = dict(U=366 * u.nm, B=438 * u.nm, V=545 * u.nm, R=641 * u.nm, I=798 * u.nm, J=1220 * u.nm,
                           H=1630 * u.nm, K=2190 * u.nm)
    _band_bandwidth = dict(U=68 * u.nm, B=98 * u.nm, V=89 * u.nm, R=220 * u.nm, I=240 * u.nm, J=300 * u.nm, H=400 * u.nm,
                          K=600 * u.nm)

    @u.quantity_input(temp=[u.Kelvin, u.Celsius], obstructor_temp=[u.Kelvin, u.Celsius])
    def __init__(self, parent: ITransmissive, transmittance: Union[SpectralQty, Callable],
                 emissivity: Union[int, float, str] = 1, temp: u.Quantity = 0 * u.K,
                 obstruction: float = 0, obstructor_temp: u.Quantity = 0 * u.K, obstructor_emissivity: float = 1):
        """
        Instantiate a new filter model

        Parameters
        ----------
        parent : ITransmissive
            The parent element of the optical component from which the electromagnetic radiation is received.
        transmittance : Union[SpectralQty, Callable]
            The spectral transmittance coefficients of the filter.
        emissivity : Union[str, int, float]
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
        super().__init__(parent, emissivity, temp, obstruction, obstructor_temp, obstructor_emissivity)
        self._transmittance = transmittance

    @classmethod
    # @u.quantity_input(temp=[u.Kelvin, u.Celsius], obstructor_temp=[u.Kelvin, u.Celsius])
    def fromBand(cls, parent: ITransmissive, band: str, emissivity: Union[str, int, float] = 1,
                 temp: u.Quantity = 0 * u.K, obstruction: float = 0, obstructor_temp: u.Quantity = 0 * u.K,
                 obstructor_emissivity: float = 1) -> "Filter":
        """
        Instantiate a new filter model from a spectral band. The filter will be modelled as bandpass filter of
        infinite order and therefore similar to a hat-function.

        Parameters
        ----------
        parent : ITransmissive
            The parent element of the optical component from which the electromagnetic radiation is received.
        band : str
            The spectral band of the filter. Can be one of [U, B, V, R, I, J, H, K].
        emissivity : Union[str, int, float]
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
        filter : Filter
            The instantiated filter object.
        """
        if band not in cls._band_central_wl.keys():
            error("Band has to be one of '[" + ", ".join(list(cls._band_central_wl.keys())) + "]'")
        return cls.fromRange(parent, cls._band_central_wl[band] - cls._band_bandwidth[band] / 2,
                             cls._band_central_wl[band] + cls._band_bandwidth[band] / 2, emissivity, temp, obstruction,
                             obstructor_temp, obstructor_emissivity)

    @classmethod
    # @u.quantity_input(temp=[u.Kelvin, u.Celsius], obstructor_temp=[u.Kelvin, u.Celsius])
    def fromFile(cls, parent: ITransmissive, transmittance: str, emissivity: Union[str, int, float] = 1,
                 temp: u.Quantity = 0 * u.K, obstruction: float = 0, obstructor_temp: u.Quantity = 0 * u.K,
                 obstructor_emissivity: float = 1) -> "Filter":
        """
        Instantiate a new filter model from a file containing the spectral transmittance coefficients.

        Parameters
        ----------
        parent : ITransmissive
            The parent element of the optical component from which the electromagnetic radiation is received.
        transmittance : str
            Path to the file containing the spectral transmittance-coefficients of the filter element.
            The format of the file will be guessed by `astropy.io.ascii.read()`.
        emissivity : Union[str, int, float]
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
        filter : Filter
            The instantiated filter object.
        """
        return cls(parent, SpectralQty.fromFile(transmittance, u.nm, u.dimensionless_unscaled), emissivity, temp,
                   obstruction, obstructor_temp, obstructor_emissivity)

    @classmethod
    # @u.quantity_input(start="length", end="length", temp=[u.Kelvin, u.Celsius], obstructor_temp=[u.Kelvin, u.Celsius])
    def fromRange(cls, parent: ITransmissive, start: u.Quantity, end: u.Quantity,
                  emissivity: Union[str, int, float] = 1, temp: u.Quantity = 0 * u.K, obstruction: float = 0,
                  obstructor_temp: u.Quantity = 0 * u.K, obstructor_emissivity: float = 1) -> "Filter":
        """
        Instantiate a new filter model from a spectral range. The filter will be modelled as bandpass filter of
        infinite order and therefore similar to a hat-function.

        Parameters
        ----------
        parent : ITransmissive
            The parent element of the optical component from which the electromagnetic radiation is received.
        start : length-quantity
            Start wavelength of the pass-band
        end : length-quantity
            End wavelength of the pass-band
        emissivity : Union[str, int, float]
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
        filter : Filter
            The instantiated filter object.
        """
        return cls(parent, cls._filter_factory(start, end), emissivity, temp,
                   obstruction, obstructor_temp, obstructor_emissivity)

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

    @staticmethod
    # @u.quantity_input(start="length", end="length")
    def _filter_factory(start: u.Quantity, end: u.Quantity):
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
        lambda : Callable
            The filter function
        """
        return lambda wl: 1 * u.dimensionless_unscaled if start <= wl <= end else 0 * u.dimensionless_unscaled
