from .ASensor import ASensor
from ..IRadiant import IRadiant
from ..Entry import Entry
from ...lib.logger import logger
from ..SpectralQty import SpectralQty
import numpy as np
from astropy import units as u
from astropy.constants import k_B
from astropy.table import QTable
from typing import Union
import os


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
        line_ind = np.where(t_signal.wl == self.__lambda_line)[0][0]
        t_sys = 2 * (t_background + self.__receiver_temp + t_signal)
        # Calculate the noise bandwidth
        delta_nu = t_signal.wl.to(u.Hz, equivalencies=u.spectral()) / (t_signal.wl / self.__common_conf.wl_delta() + 1)
        snr = []
        for exp_time_ in exp_time if exp_time.size > 1 else [exp_time]:
            # Calculate the RMS background temperature
            if self.__n_on is None:
                t_rms = 2 * t_sys * self.__kappa / np.sqrt(exp_time_ * delta_nu)
            else:
                t_rms = t_sys * self.__kappa * np.sqrt(1 + 1 / np.sqrt(self.__n_on)) / np.sqrt(exp_time_ * delta_nu)
            # Calculate the SNR
            snr_ = t_signal / t_rms
            snr.append(snr_.qty[line_ind])
            # Print details
            self.__printDetails(t_sys.qty[line_ind], delta_nu[line_ind], t_rms.qty[line_ind], t_signal.qty[line_ind],
                                "t_exp=%.2f s: " % exp_time_.value)
            self.__output(t_signal, t_background, t_rms, "texp_%.2f" % exp_time_.value, snr=snr_)
        return u.Quantity(snr) if len(snr) > 1 else u.Quantity(snr[0])

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
        line_ind = np.where(t_signal.wl == self.__lambda_line)[0][0]
        t_sys = 2 * (t_background + self.__receiver_temp)
        # Calculate the noise bandwidth
        delta_nu = t_signal.wl.to(u.Hz, equivalencies=u.spectral()) / (t_signal.wl / self.__common_conf.wl_delta() + 1)
        exp_time = []
        for snr_ in snr if snr.size > 1 else [snr]:
            # Calculate the RMS background temperature
            t_rms = t_signal / snr_
            # Calculate the exposure time
            if self.__n_on is None:
                exp_time_ = ((2 * t_sys * self.__kappa / t_rms) ** 2 / delta_nu)
            else:
                exp_time_ = ((t_sys * self.__kappa / t_rms) ** 2 *
                             (1 + 1 / np.sqrt(self.__n_on)) / delta_nu)
            exp_time_ = SpectralQty(exp_time_.wl, exp_time_.qty.decompose())
            exp_time.append(exp_time_.qty[line_ind])
            # Print details
            self.__printDetails(t_sys.qty[line_ind], delta_nu[line_ind], t_rms.qty[line_ind], t_signal.qty[line_ind],
                                "SNR=%.2f: " % snr_.value)
            self.__output(t_signal, t_background, t_rms, "snr_%.2f" % snr_.value, exp_time=exp_time_)
        return u.Quantity(exp_time) if len(exp_time) > 1 else u.Quantity(exp_time[0])

    # @u.quantity_input(exp_time="time", snr=u.dimensionless_unscaled,
    #                   target_brightness=[u.mag, u.mag / u.sr])
    def calcSensitivity(self, background: SpectralQty, signal: SpectralQty, obstruction: float, exp_time: u.Quantity,
                        snr: u.Quantity, target_brightness: u.Quantity) -> [u.mag, u.mag / u.sr]:
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
            The target brightness in mag or mag / sr.

        Returns
        -------
        sensitivity: Quantity
            The sensitivity as limiting apparent star magnitude in mag.
        """
        # Calculate the signal and background temperatures
        t_signal, t_background = self.calcTemperatures(background, signal, obstruction)
        line_ind = np.where(t_signal.wl == self.__lambda_line)[0][0]
        t_sys = 2 * (t_background + self.__receiver_temp)
        # Calculate the noise bandwidth
        delta_nu = t_signal.wl.to(u.Hz, equivalencies=u.spectral()) / (t_signal.wl / self.__common_conf.wl_delta() + 1)
        sensitivity = []
        for snr_, exp_time_ in zip(snr, exp_time) if snr.size > 1 else zip([snr], [exp_time]):
            # Calculate the RMS background temperature
            if self.__n_on is None:
                t_rms = 2 * t_sys * self.__kappa / np.sqrt(exp_time_ * delta_nu)
            else:
                t_rms = t_sys * self.__kappa * np.sqrt(1 + 1 / np.sqrt(self.__n_on)) / np.sqrt(exp_time_ * delta_nu)
            # Calculate the limiting signal temperature
            t_signal_lim = t_rms * snr_
            # Calculate the sensitivity
            signal_ratio = t_signal_lim / t_signal
            sensitivity_ = SpectralQty(signal_ratio.wl,
                                       target_brightness - 2.5 * np.log10(signal_ratio.qty) * target_brightness.unit)
            sensitivity.append(sensitivity_.qty[line_ind])
            # Print details
            self.__printDetails(t_sys.qty[line_ind], delta_nu[line_ind], t_rms.qty[line_ind],
                                t_signal_lim.qty[line_ind], "SNR=%.2f t_exp=%.2f s: " % (snr_.value, exp_time_.value))
            self.__output(t_signal, t_background, t_rms, "snr_%.2f_texp_%.2f" % (snr_.value, exp_time_.value),
                          sensitivity=sensitivity_)
        return u.Quantity(sensitivity) if len(sensitivity) > 1 else u.Quantity(sensitivity[0])

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

    @u.quantity_input(signal=u.electron, background=u.electron, read_noise=u.electron ** 0.5, dark=u.electron)
    def __output(self, t_signal: SpectralQty, t_background: SpectralQty, t_rms: SpectralQty,
                 name: str, snr: SpectralQty = None, exp_time: SpectralQty = None, sensitivity: SpectralQty = None):
        """
        Write the signal and the noise in electrons to files.

        Parameters
        ----------
        t_signal : SpectralQty
            The signal temperature in Kelvins.
        t_background : SpectralQty
            The background temperature in Kelvins.
        t_rms : SpectralQty
            The RMS noise temperature in Kelvins.
        name : str
            The name of the configuration.
        snr : SpectralQty
            The calculated signal-to-noise ratio per wavelength.
        exp_time : SpectralQty
            The calculated exposure time  per wavelength.
        sensitivity : SpectralQty
            The calculated sensitivity per wavelength.

        Returns
        -------
        """
        # Concatenate the paths
        path = os.path.join(self.__common_conf.output.path, name)
        try:
            os.makedirs(path, exist_ok=True)
        except FileExistsError:
            logger.warning("Output directory '" + path + "' already exists.")

        res = QTable([t_signal.wl, t_signal.qty, t_background.qty, t_rms.qty],
                     names=('Wavelength [' + t_signal.wl.unit.to_string() + ']',
                            'Signal Temperature [' + t_signal.qty.unit.to_string() + ']',
                            'Background Temperature [' + t_background.qty.unit.to_string() + ']',
                            'RMS Noise Temperature [' + t_rms.qty.unit.to_string() + ']'),
                     meta={'name': 'first table'})
        if snr is not None:
            res['SNR [-]'] = snr.qty
        if exp_time is not None:
            res['Exposure Time [' + exp_time.qty.unit.to_string() + ']'] = exp_time.qty
        if sensitivity is not None:
            res['Sensitivity [' + sensitivity.qty.unit.to_string() + ']'] = sensitivity.qty
        res.write(os.path.join(path, "result.csv"), format='ascii.csv', overwrite=True)

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
        t_signal : SpectralQty
            The spectral signal temperature in Kelvins.
        t_background : SpectralQty
            The spectral signal temperature in Kelvins.
        """
        logger.info("Calculating the system temperature.")
        # Add desired wavelength to wavelength bins
        wl_bins = np.sort(np.append(self.__common_conf.wl_bins(), self.__lambda_line)).view(u.Quantity)
        signal = signal.rebin(wl_bins)
        background = background.rebin(wl_bins)
        background = SpectralQty(background.wl, background.qty.to(u.W / (u.m ** 2 * u.Hz * u.sr),
                                                                    equivalencies=u.spectral_density(
                                                                        background.wl)))
        t_background = background * (
                    self.__main_beam_efficiency * background.wl ** 2 / (2 * k_B) * self.__eta_fss * u.sr)
        t_background = SpectralQty(t_background.wl, t_background.qty.decompose())
        # Calculate the incoming photon current of the target
        logger.info("Calculating the signal temperature.")
        size = "extended" if signal.qty.unit.is_equivalent(u.W / (u.m ** 2 * u.nm * u.sr)) else "point"
        if size == "point":
            signal = SpectralQty(signal.wl, signal.qty.to(u.W / (u.m ** 2 * u.Hz),
                                                          equivalencies=u.spectral_density(signal.wl)))
            t_signal = signal * (self.__aperture_efficiency * self.__common_conf.d_aperture() ** 2 *
                                 np.pi / 4 / (2 * k_B) * self.__eta_fss)
            t_signal = SpectralQty(t_signal.wl, t_signal.qty.decompose())
        else:
            signal = SpectralQty(signal.wl, signal.qty.to(u.W / (u.m ** 2 * u.Hz * u.sr),
                                                          equivalencies=u.spectral_density(signal.wl)))
            t_signal = signal * (self.__main_beam_efficiency * signal.wl ** 2 / (
                    2 * k_B) * self.__eta_fss * u.sr)
            t_signal = SpectralQty(t_signal.wl, t_signal.qty.decompose())
        logger.debug("Spectral signal temperature")
        logger.debug(t_signal)
        logger.debug("Target size: " + size)
        logger.debug("Obstruction: %.2f" % obstruction)
        logger.debug("Spectral background temperature")
        logger.debug(t_background)
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
