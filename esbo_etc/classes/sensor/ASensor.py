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
    def getSNR(self, exp_time: u.Quantity) -> u.dimensionless_unscaled:
        """
        Calculate the signal to noise ratio (SNR) for the given exposure time.

        Parameters
        ----------
        exp_time : time-Quantity
            The exposure time to calculate the SNR for.

        Returns
        -------
        snr : Quantity
            The calculated SNR
        """
        pass

    @abstractmethod
    @u.quantity_input(snr=u.dimensionless_unscaled)
    def getExpTime(self, snr: u.Quantity) -> u.s:
        """
        Calculate the necessary exposure time in order to achieve the given SNR.

        Parameters
        ----------
        snr : Quantity
            The SNR for which the necessary exposure time shall be calculated.

        Returns
        -------
        exp_time : Quantity
            The necessary exposure time in seconds.
        """
        pass

    @abstractmethod
    @u.quantity_input(exp_time="time", snr=u.dimensionless_unscaled, target_brightness=u.mag)
    def getSensitivity(self, exp_time: u.Quantity, snr: u.Quantity, target_brightness: u.Quantity) -> u.mag:
        """
        Calculate the sensitivity of the telescope detector combination.

        Parameters
        ----------
        exp_time : Quantity
            The exposure time in seconds.
        snr : Quantity
            The SNR for which the sensitivity time shall be calculated.
        target_brightness : Quantity
            The target brightness in magnitudes.

        Returns
        -------
        sensitivity: Quantity
            The sensitivity as limiting apparent star magnitude in mag.
        """
        pass

    @staticmethod
    def check_config(sensor: Entry, conf: Entry) -> Union[None, str]:
        """
        Check the configuration for this class

        Parameters
        ----------
        sensor : Entry
            The configuration entry to be checked.
        conf: Entry
            The complete configuration.

        Returns
        -------
        mes : Union[None, str]
            The error message of the check. This will be None if the check was successful.
        """
        pass
