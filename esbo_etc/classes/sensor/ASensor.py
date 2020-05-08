from ..IRadiant import IRadiant
import astropy.units as u
from abc import abstractmethod
from ..Entry import Entry
from typing import Union


class ASensor:
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
            The error message of the check. This will be None if the check was succesful.
        """
        pass
