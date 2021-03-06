from esbo_etc.classes.optical_component.AOpticalComponent import AOpticalComponent
from esbo_etc.classes.IRadiant import IRadiant
from esbo_etc.classes.SpectralQty import SpectralQty
from abc import abstractmethod
import astropy.units as u
from astropy.modeling.models import BlackBody
from typing import Union, Callable
from ..Entry import Entry


class AHotOpticalComponent(AOpticalComponent):
    """
    Abstract super class for an optical component with thermal emission
    """
    @abstractmethod
    @u.quantity_input(wl_bins='length', temp=[u.Kelvin, u.Celsius], obstruction_temp=[u.Kelvin, u.Celsius])
    def __init__(self, parent: IRadiant, emissivity: Union[SpectralQty, int, float, str], temp: u.Quantity,
                 obstruction: float = 0, obstructor_temp: u.Quantity = 0 * u.K, obstructor_emissivity: float = 1):
        """
        Initialize a new optical component with thermal emission

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received.
        emissivity : Union[SpectralQty, int, float, str]
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
        # Initialize super class
        super().__init__(parent, obstruction=obstruction, obstructor_temp=obstructor_temp,
                         obstructor_emissivity=obstructor_emissivity)
        if temp > 0 * u.K:
            # Create noise from black body model
            if isinstance(emissivity, SpectralQty):
                bb = self.__gb_factory(temp)
                self.__noise = SpectralQty(emissivity.wl, bb(emissivity.wl)) * emissivity
            elif isinstance(emissivity, str):
                try:
                    em = float(emissivity)
                    bb = self.__gb_factory(temp, em)
                    self.__noise = bb
                except ValueError:
                    em = SpectralQty.fromFile(emissivity, u.nm, u.dimensionless_unscaled)
                    bb = self.__gb_factory(temp)
                    self.__noise = SpectralQty(em.wl, bb(em.wl)) * em
            else:
                bb = self.__gb_factory(temp, emissivity)
                self.__noise = bb
        else:
            self.__noise = 0

    def _ownNoise(self) -> Union[SpectralQty, Callable[[u.Quantity], u.Quantity], int, float]:
        """
        Calculate the noise created by the optical component

        Returns
        -------
        noise : Union[SpectralQty, Callable[[u.Quantity], u.Quantity], int, float]
            The noise created by the optical component
        """
        return self.__noise

    @staticmethod
    @u.quantity_input(temp=[u.Kelvin, u.Celsius])
    def __gb_factory(temp: u.Quantity, em: Union[int, float] = 1):
        """
        Factory for a grey body lambda-function.

        Parameters
        ----------
        temp : Quantity in Kelvin / Celsius
            The temperature fo the grey body.
        em : Union[int, float]
            Emissivity of the the grey body

        Returns
        -------
        bb : Callable
            The lambda function for the grey body.
        """
        bb = BlackBody(temperature=temp, scale=em * u.W / (u.m ** 2 * u.nm * u.sr))
        return lambda wl: bb(wl)

    @staticmethod
    @abstractmethod
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
        pass
