from ..IRadiant import IRadiant
import astropy.units as u
from abc import abstractmethod


class Sensor:
    """
    Abstract super class for sensor models
    """
    def __init__(self, parent: IRadiant):
        """
        Initialize a new sensor

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received
        """
        self._parent = parent

    @abstractmethod
    @u.quantity_input(exp_time="time")
    def getSNR(self, exp_time: u.Quantity):
        """
        Calculate the signal to noise ratio (SNR) for the given exposure time.

        Parameters
        ----------
        exp_time : time-Quantity
            The exposure time to calculate the SNR for.

        Returns
        -------
        snr : float
            The calculated SNR
        """
        pass

    @abstractmethod
    def getExpTime(self, snr: float):
        """
        Calculate the necessary exposure time in order to achieve the given SNR.

        Parameters
        ----------
        snr : float
            The SNR for which the necessary exposure time shall be calculated.

        Returns
        -------
        exp_time : Quantity
            The necessary exposure time in seconds.
        """
        pass
