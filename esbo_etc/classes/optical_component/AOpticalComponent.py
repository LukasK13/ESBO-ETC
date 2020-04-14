from ..ITransmissive import ITransmissive
from abc import abstractmethod
from ..SpectralQty import SpectralQty
from esbo_etc.lib.helpers import error
import astropy.units as u
from astropy.modeling.models import BlackBody


class AOpticalComponent(ITransmissive):
    """
    Abstract super class for an optical component
    """

    @abstractmethod
    @u.quantity_input(obstructor_temp=[u.K, u.Celsius])
    def __init__(self, parent: ITransmissive, transreflectivity: SpectralQty = None,
                 noise: SpectralQty = None, obstruction: float = 0, obstructor_temp: u.Quantity = 0 * u.K,
                 obstructor_emissivity: float = 0):
        """
        Initialize a new optical component

        Parameters
        ----------
        parent : ITransmissive
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
        self._parent = parent
        if transreflectivity:
            self._transreflectivity = transreflectivity
        if noise:
            self._noise = noise
        self._obstruction = obstruction
        self._obstructor_temp = obstructor_temp
        self._obstructor_emissivity = obstructor_emissivity

    def calcSignal(self) -> SpectralQty:
        """
        Calculate the spectral flux density of the target's signal

        Returns
        -------
        signal : SpectralQty
            The spectral flux density of the target's signal
        """
        return self.propagate(self._parent.calcSignal()) * (1 - self._obstruction)

    def calcNoise(self) -> SpectralQty:
        """
        Calculate the spectral radiance of the target's noise

        Returns
        -------
        noise : SpectralQty
            The spectral radiance of the target's noise
        """
        parent = self.propagate(self._parent.calcNoise())
        if self._obstructor_temp > 0 * u.K:
            bb = BlackBody(temperature=self._obstructor_temp, scale=1. * u.W / (u.m ** 2 * u.nm * u.sr))
            obstructor = bb(parent.wl) * self._obstructor_emissivity
            return parent * (1. - self._obstruction) + obstructor * self._obstruction + self.ownNoise()
        else:
            return parent * (1. - self._obstruction) + self.ownNoise()

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
        if hasattr(self, "_transreflectivity"):
            return sqty * self._transreflectivity
        else:
            error("Transreflectivity not given. Method propagate() needs to be implemented.")

    def ownNoise(self) -> SpectralQty:
        """
        Calculate the noise created by the optical component

        Returns
        -------
        sqty : SpectralQty
            The noise created by the optical component
        """
        if hasattr(self, "_noise"):
            return self._noise
        else:
            error("noise not given. Method ownNoise() needs to be implemented.")
