from astropy import units as u
from .ASensor import ASensor
from ..IRadiant import IRadiant
from ..Entry import Entry
import numpy as np
from astropy.constants import k_B
from typing import Union
from ...lib.logger import logger
from ..SpectralQty import SpectralQty


class Heterodyne(ASensor):
    """
    A class for modelling the behaviour of a superheterodyne spectrometer.
    """

    def __init__(self, parent: IRadiant, aperture_efficiency: float, main_beam_efficiency: float,
                 receiver_temp: u.Quantity, eta_fss: float, lambda_line: u.Quantity, kappa: float, common_conf: Entry,
                 n_on: float = None):
        """
        Initialize a new heterodyne detector

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received.
        aperture_efficiency : float
            The aperture efficiency of the antenna.
        main_beam_efficiency : float
            The main beam efficiency of the telescope.
        receiver_temp : u.Quantity in Kelvins
            The intrinsic noise temperature of all receiver components.
        eta_fss : float
            The forward scattering efficiency of the antenna.
        lambda_line : u.Quantity
            The wavelength to be used for calculating the SNR.
        kappa : float
            The backend degradation factor.
        common_conf : Entry
            The common-Entry of the configuration.
        n_on : float
            The number of on source observations.
        """
        self.__aperture_efficiency = aperture_efficiency
        self.__main_beam_efficiency = main_beam_efficiency
        self.__receiver_temp = receiver_temp
        self.__eta_fss = eta_fss
        self.__lambda_line = lambda_line
        self.__kappa = kappa
        self.__common_conf = common_conf
        self.__n_on = n_on
        super().__init__(parent)

    @u.quantity_input(exp_time="time")
    def calcSNR(self, background: SpectralQty, signal: SpectralQty, obstruction: float,
                exp_time: u.Quantity) -> u.dimensionless_unscaled:
        """
        Calculate the signal to background ratio (SNR) for the given exposure time using the CCD-equation.

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
            The calculated SNR as dimensionless quantity
        """
        # Calculate the signal and background temperatures
        t_signal, t_background = self.calcTemperatures(background, signal, obstruction)
        t_sys = 2 * (t_background + self.__receiver_temp)
        # Calculate the noise bandwidth
        delta_nu = self.__lambda_line.to(u.Hz, equivalencies=u.spectral()) / (
                self.__lambda_line / self.__common_conf.wl_delta() + 1)
        # Calculate the RMS background temperature
        if self.__n_on is None:
            t_rms = 2 * t_sys * self.__kappa / np.sqrt(exp_time * delta_nu)
        else:
            t_rms = t_sys * self.__kappa * np.sqrt(1 + 1 / np.sqrt(self.__n_on)) / np.sqrt(exp_time * delta_nu)
        # Calculate the SNR
        snr = t_signal / t_rms
        # Print details
        if exp_time.size > 1:
            for i in range(exp_time.size):
                self.__printDetails(t_sys, delta_nu, t_rms[i], t_signal, "t_exp=%.2f s: " % exp_time[i].value)
        else:
            self.__printDetails(t_sys, delta_nu, t_rms, t_signal, "t_exp=%.2f s: " % exp_time.value)
        return snr

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
            The SNR for which the necessary exposure time shall be calculated as dimensionless quantity.

        Returns
        -------
        exp_time : Quantity
            The necessary exposure time in seconds.
        """
        # Calculate the signal and background temperatures
        t_signal, t_background = self.calcTemperatures(background, signal, obstruction)
        t_sys = 2 * (t_background + self.__receiver_temp)
        # Calculate the noise bandwidth
        delta_nu = self.__lambda_line.to(u.Hz, equivalencies=u.spectral()) / (
                self.__lambda_line / self.__common_conf.wl_delta() + 1)
        # Calculate the RMS background temperature
        t_rms = t_signal / snr
        # Calculate the exposure time
        if self.__n_on is None:
            exp_time = ((2 * t_sys * self.__kappa / t_rms) ** 2 / delta_nu).decompose()
        else:
            exp_time = ((t_sys * self.__kappa / t_rms) ** 2 * (1 + 1 / np.sqrt(self.__n_on)) / delta_nu).decompose()
        # Print details
        if snr.size > 1:
            for i in range(snr.size):
                self.__printDetails(t_sys, delta_nu, t_rms[i], t_signal, "SNR=%.2f: " % snr[i].value)
        else:
            self.__printDetails(t_sys, delta_nu, t_rms, t_signal, "SNR=%.2f: " % snr.value)
        return exp_time

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
        # Calculate the signal and background temperatures
        t_signal, t_background = self.calcTemperatures(background, signal, obstruction)
        t_sys = 2 * (t_background + self.__receiver_temp)
        # Calculate the noise bandwidth
        delta_nu = self.__lambda_line.to(u.Hz, equivalencies=u.spectral()) / (
                self.__lambda_line / self.__common_conf.wl_delta() + 1)
        # Calculate the RMS background temperature
        if self.__n_on is None:
            t_rms = 2 * t_sys * self.__kappa / np.sqrt(exp_time * delta_nu)
        else:
            t_rms = t_sys * self.__kappa * np.sqrt(1 + 1 / np.sqrt(self.__n_on)) / np.sqrt(exp_time * delta_nu)
        # Calculate the limiting signal temperature
        t_signal_lim = t_rms * snr
        # Print details
        if snr.size > 1:
            for i in range(snr.size):
                self.__printDetails(t_sys, delta_nu, t_rms[i], t_signal_lim[i],
                                    "SNR=%.2f t_exp=%.2f s: " % (snr[i].value, exp_time[i].value))
        else:
            self.__printDetails(t_sys, delta_nu, t_rms, t_signal_lim,
                                "SNR=%.2f t_exp=%.2f s: " % (snr.value, exp_time.value))
        return target_brightness - 2.5 * np.log10(t_signal_lim / t_signal) * u.mag

    @u.quantity_input(t_sys=u.K, delta_nu=u.Hz, t_rms=u.K, t_signal=u.K)
    def __printDetails(self, t_sys: u.Quantity, delta_nu: u.Quantity, t_rms: u.Quantity,
                       t_signal: u.Quantity, prefix: str = ""):
        """
        Print details on the signal and noise composition.

        Parameters
        ----------
        t_sys : Quantity
            The system temperature.
        delta_nu : Quantity
            The noise bandwidth.
        t_rms : Quantity
            The RMS antenna temperature.
        t_signal : Quantity
            The antenna temperature.
        prefix : str
            The prefix to be used for printing.

        Returns
        -------
        """
        logger.info("-------------------------------------------------------------------------------------------------")
        logger.info(prefix + "System temperature:        %1.2e K" % t_sys.value)
        logger.info(prefix + "Noise bandwidth:           %1.2e K" % delta_nu.value)
        logger.info(prefix + "RMS antenna temperature:   %1.2e K" % t_rms.value)
        logger.info(prefix + "Antenna temperature:       %1.2e K" % t_signal.value)
        logger.info("-------------------------------------------------------------------------------------------------")

    def calcTemperatures(self, background: SpectralQty, signal: SpectralQty, obstruction: float):
        """
        Calculate the noise temperatures of the signal and the background radiation.

        Parameters
        ----------
        background : SpectralQty
            The received background radiation
        signal : SpectralQty
            The received signal radiation
        obstruction : float
            The obstruction factor of the aperture as ratio A_ob / A_ap

        Returns
        -------
        t_signal : u.Quantity
            The signal temperature in Kelvins.
        t_background : u.Quantity
            The background temperature in Kelvins.
        """
        logger.info("Calculating the system temperature.")
        t_background = (background.rebin(self.__lambda_line).qty.to(
            u.W / (u.m ** 2 * u.Hz * u.sr), equivalencies=u.spectral_density(self.__lambda_line)) *
                        self.__lambda_line ** 2 / (2 * k_B) * u.sr).decompose()
        # Calculate the incoming photon current of the target
        logger.info("Calculating the signal temperature.")
        size = "extended" if signal.qty.unit.is_equivalent(u.W / (u.m ** 2 * u.nm * u.sr)) else "point"
        if size == "point":
            signal = signal.rebin(self.__lambda_line).qty.to(u.W / (u.m ** 2 * u.Hz),
                                                             equivalencies=u.spectral_density(self.__lambda_line))
            t_signal = (signal * self.__aperture_efficiency * self.__common_conf.d_aperture() ** 2 *
                        np.pi / 4 / (2 * k_B) * self.__eta_fss).decompose()
        else:
            signal = signal.rebin(self.__lambda_line).qty.to(u.W / (u.m ** 2 * u.Hz * u.sr),
                                                             equivalencies=u.spectral_density(self.__lambda_line))
            t_signal = (signal * u.sr * self.__main_beam_efficiency * self.__lambda_line ** 2 / (
                    2 * k_B) * self.__eta_fss).decompose()
        logger.debug("Signal temperature: %1.2e K" % t_signal.value)
        logger.debug("Target size: " + size)
        logger.debug("Obstruction: %.2f" % obstruction)
        logger.debug("Background temperature: %1.2e K" % t_background.value)
        return t_signal, t_background

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
        if not hasattr(sensor, "aperture_efficiency"):
            return "Missing container 'aperture_efficiency'."
        mes = sensor.aperture_efficiency.check_float("val")
        if mes is not None:
            return "aperture_efficiency: " + mes
        if not hasattr(sensor, "main_beam_efficiency"):
            return "Missing container 'main_beam_efficiency'."
        mes = sensor.main_beam_efficiency.check_float("val")
        if mes is not None:
            return "main_beam_efficiency: " + mes
        if not hasattr(sensor, "receiver_temp"):
            return "Missing container 'receiver_temp'."
        mes = sensor.receiver_temp.check_quantity("val", u.K)
        if mes is not None:
            return "receiver_temp: " + mes
        if not hasattr(sensor, "eta_fss"):
            return "Missing container 'eta_fss'."
        mes = sensor.eta_fss.check_float("val")
        if mes is not None:
            return "eta_fss: " + mes
        if not hasattr(sensor, "lambda_line"):
            return "Missing container 'lambda_line'."
        mes = sensor.lambda_line.check_quantity("val", u.nm)
        if mes is not None:
            return "lambda_line: " + mes
        if not hasattr(sensor, "kappa"):
            return "Missing container 'kappa'."
        mes = sensor.kappa.check_float("val")
        if mes is not None:
            return "kappa: " + mes
        if hasattr(sensor, "n_on") and isinstance(sensor.n_on, Entry):
            mes = sensor.n_on.check_float("val")
            if mes is not None:
                return "n_on: " + mes
