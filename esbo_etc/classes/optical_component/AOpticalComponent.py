from ..IRadiant import IRadiant
from ..SpectralQty import SpectralQty
from ...lib.helpers import error
from abc import abstractmethod
import astropy.units as u
from astropy.modeling.models import BlackBody
from typing import Union, Callable, Tuple
from logging import info, debug
from ..Entry import Entry


class AOpticalComponent(IRadiant):
    """
    Abstract super class for an optical component
    """

    @abstractmethod
    @u.quantity_input(obstructor_temp=[u.K, u.Celsius])
    def __init__(self, parent: IRadiant, transreflectivity: Union[SpectralQty, int, float, u.Quantity] = None,
                 noise: Union[SpectralQty, int, float, u.Quantity] = None, obstruction: float = 0,
                 obstructor_temp: u.Quantity = 0 * u.K, obstructor_emissivity: float = 1):
        """
        Initialize a new optical component

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received
        transreflectivity : SpectralQty
            The spectral transmission / reflectivity coefficient of the component. This coefficient is multiplied with
            the incoming radiation from the parent element in order to propagate the incoming radiation through the
            optical component.
        noise : SpectralQty
            The noise created by the optical component as spectral radiance. This noise will be added to the propagated
            incoming noise in order to calculate the overall noise.
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
        self.__parent = parent
        if transreflectivity:
            self.__transreflectivity = transreflectivity
        if noise:
            self.__noise = noise
        self.__obstruction = obstruction
        self.__obstructor_temp = obstructor_temp
        self.__obstructor_emissivity = obstructor_emissivity

    def calcSignal(self) -> Tuple[SpectralQty, str]:
        """
        Calculate the spectral flux density of the target's signal

        Returns
        -------
        signal : SpectralQty
            The spectral flux density of the target's signal
        size : str
            The size of the target.
        """
        signal, size = self.__parent.calcSignal()
        info("Calculating signal for class '" + self.__class__.__name__ + "'.")
        signal = self._propagate(signal) * (1 - self.__obstruction)
        debug(signal)
        return signal, size

    def calcBackground(self) -> SpectralQty:
        """
        Calculate the spectral radiance of the background

        Returns
        -------
        background : SpectralQty
            The spectral radiance of the background
        """
        parent = self.__parent.calcBackground()
        info("Calculating background for class '" + self.__class__.__name__ + "'.")
        parent = self._propagate(parent)
        if self.__obstructor_temp > 0 * u.K:
            bb = BlackBody(temperature=self.__obstructor_temp, scale=1. * u.W / (u.m ** 2 * u.nm * u.sr))
            obstructor = bb(parent.wl) * self.__obstructor_emissivity
            background = parent * (1. - self.__obstruction) + obstructor * self.__obstruction
        else:
            background = parent * (1. - self.__obstruction)
        background = background + self._ownNoise()
        debug(background)
        return background

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
        try:
            return rad * self.__transreflectivity
        except AttributeError:
            error("Transreflectivity not given. Method propagate() needs to be implemented.")

    def _ownNoise(self) -> Union[SpectralQty, Callable[[u.Quantity], u.Quantity], int, float]:
        """
        Calculate the noise created by the optical component

        Returns
        -------
        noise : Union[SpectralQty, Callable[[u.Quantity], u.Quantity], int, float]
            The noise created by the optical component
        """
        try:
            return self.__noise
        except AttributeError:
            error("noise not given. Method ownNoise() needs to be implemented.")

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
