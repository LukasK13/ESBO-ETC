from ..ITransmissive import ITransmissive
from abc import abstractmethod
from ..SpectralQty import SpectralQty
import copy


class AOpticalComponent(ITransmissive):
    """
    Abstract super class for an optical component
    """

    @abstractmethod
    def __init__(self, parent: ITransmissive, transreflectivity: SpectralQty = None,
                 noise: SpectralQty = None, obstruction: float = 0):
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
            The noise created by the optical component. This noise will be added to the propagated incoming noise in
            order to calculate the overall noise.
        obstruction : float
            The additional obstruction factor of the optical component. 0 means the component is not obstructed, 1
            denotes a completely obstructed component with therefore no incoming flux. It is important to note, that
            the obstruction factor reflects the obstruction of the optical component additionally to the obstruction
            factors of the prior elements in the beam.
        """
        self._parent = parent
        if transreflectivity:
            self._transreflectivity = transreflectivity
        if noise:
            self._noise = noise
        self._obstruction = obstruction

    def calcSignal(self) -> SpectralQty:
        """
        Calculate the spectral flux density of the target's signal

        Returns
        -------
        signal : SpectralQty
            The spectral flux density of the target's signal
        """
        return self.propagate(copy.deepcopy(self._parent.calcSignal())).multiply(1 - self._obstruction)

    def calcNoise(self) -> SpectralQty:
        """
        Calculate the spectral radiance of the target's noise

        Returns
        -------
        noise : SpectralQty
            The spectral radiance of the target's noise
        """
        return self.propagate(copy.deepcopy(self._parent.calcNoise())).add(self.ownNoise())

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
        return sqty.multiply(self._transreflectivity)

    def ownNoise(self) -> SpectralQty:
        """
        Calculate the noise created by the optical component

        Returns
        -------
        sqty : SpectralQty
            The noise created by the optical component
        """
        return self._noise
