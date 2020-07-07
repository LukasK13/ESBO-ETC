from ..IRadiant import IRadiant
import astropy.units as u
from abc import abstractmethod
from ..Entry import Entry
from typing import Union
from ..SpectralQty import SpectralQty
from ...lib.logger import logger


class ASensor:
    """
    Abstract super class for sensor models
    """
    @abstractmethod
    def __init__(self, parent: IRadiant):
        """
        Initialize a new sensor

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received
        """
        self._parent = parent

    def __calcIncomingRadiation(self):
        """
        Trigger the radiation transportation pipeline in order to calculate the received radiation.

        Returns
        -------
        background : SpectralQty
            The received background radiation
        signal : SpectralQty
            The received signal radiation
        obstruction : float
            The obstruction factor of the aperture as ratio A_ob / A_ap
        """
        logger.info("Calculating incoming background radiation", extra={"spinning": True})
        background = self._parent.calcBackground()
        logger.info("Calculating incoming signal radiation", extra={"spinning": True})
        signal, obstruction = self._parent.calcSignal()
        return background, signal, obstruction

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
        background, signal, obstruction = self.__calcIncomingRadiation()
        return self.calcSNR(background, signal, obstruction, exp_time)

    @abstractmethod
    @u.quantity_input(exp_time="time")
    def calcSNR(self, background: SpectralQty, signal: SpectralQty, obstruction: float,
                exp_time: u.Quantity) -> u.dimensionless_unscaled:
        """
        Calculate the signal to noise ratio (SNR) for the given exposure time.

        Parameters
        ----------
        background : SpectralQty
            The received background radiation
        signal : SpectralQty
            The received signal radiation
        obstruction : float
            The obstruction factor of the aperture as ratio A_ob / A_ap
        exp_time : time-Quantity
            The exposure time to calculate the SNR for.

        Returns
        -------
        snr : Quantity
            The calculated SNR
        """
        pass

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
        background, signal, obstruction = self.__calcIncomingRadiation()
        return self.calcExpTime(background, signal, obstruction, snr)

    @abstractmethod
    @u.quantity_input(snr=u.dimensionless_unscaled)
    def calcExpTime(self, background: SpectralQty, signal: SpectralQty, obstruction: float, snr: u.Quantity) -> u.s:
        """
        Calculate the necessary exposure time in order to achieve the given SNR.

        Parameters
        ----------
        background : SpectralQty
            The received background radiation
        signal : SpectralQty
            The received signal radiation
        obstruction : float
            The obstruction factor of the aperture as ratio A_ob / A_ap
        snr : Quantity
            The SNR for which the necessary exposure time shall be calculated.

        Returns
        -------
        exp_time : Quantity
            The necessary exposure time in seconds.
        """
        pass

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
        background, signal, obstruction = self.__calcIncomingRadiation()
        return self.calcSensitivity(background, signal, obstruction, exp_time, snr, target_brightness)

    @abstractmethod
    @u.quantity_input(exp_time="time", snr=u.dimensionless_unscaled, target_brightness=u.mag)
    def calcSensitivity(self, background: SpectralQty, signal: SpectralQty, obstruction: float, exp_time: u.Quantity,
                        snr: u.Quantity, target_brightness: u.Quantity) -> u.mag:
        """
        Calculate the sensitivity of the telescope detector combination.

        Parameters
        ----------
        background : SpectralQty
            The received background radiation
        signal : SpectralQty
            The received signal radiation
        obstruction : float
            The obstruction factor of the aperture as ratio A_ob / A_ap
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
    @abstractmethod
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
