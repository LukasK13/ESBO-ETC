from astropy import units as u
from .ASensor import ASensor
from ..IRadiant import IRadiant
from ..Entry import Entry
import numpy as np
from typing import Union, Tuple
from ..psf.Airy import Airy
from ..psf.Zemax import Zemax
from ..SpectralQty import SpectralQty
from .PixelMask import PixelMask
import astropy.constants as const
from logging import info, warning, debug, getLogger
import enlighten


class Imager(ASensor):
    """
    A class for modelling a Image-sensor
    """
    __encircled_energy: Union[str, float, u.Quantity]

    @u.quantity_input(pixel_geometry=u.pixel, pixel_size="length", read_noise=u.electron ** 0.5 / u.pix,
                      center_offset=u.pix, dark_current=u.electron / u.pix / u.second, well_capacity=u.electron)
    def __init__(self, parent: IRadiant, quantum_efficiency: Union[str, u.Quantity],
                 pixel_geometry: u.Quantity, pixel_size: u.Quantity, read_noise: u.Quantity, dark_current: u.Quantity,
                 well_capacity: u.Quantity, f_number: Union[int, float], common_conf: Entry,
                 center_offset: u.Quantity = np.array([0, 0]) << u.pix, shape: str = "circle",
                 contained_energy: Union[str, int, float] = "FWHM", contained_pixels: u.Quantity = None):
        """
        Initialize a new Image-sensor model.
        Initialize a new Image-sensor model.

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received.
        quantum_efficiency : Union[str, u.Quantity]
            The quantum efficiency of the detector. This can be either the path to the file containing the values of
            the spectral quantum efficiency or the overall quantum efficiency as astropy quantity.
        pixel_geometry : u.Quantity
            The geometry of the pixel array as Quantity in pixels with two entries:
            [number of pixels in x-direction, number of pixels in y-direction]
        pixel_size : length-Quantity
            The edge length of a pixel (assumed to be square).
        read_noise : Quantity
            The RMS-read noise per detector pixel in electrons^0.5 / pixel.
        dark_current : Quantity
            The dark current of a detector pixel in electrons / (pixels * s).
        well_capacity : Quantity
            The pixel's well capacity in electrons.
        f_number : Union[int, float]
            The f-number of the optical system.
        common_conf : Entry
            The common-Entry of the configuration.
        center_offset : u.Quantity
            The offset of the PSF-center relative to the center of the detector array as length-quantity with two
            entries: [offset in x-direction, offset in y-direction]
        shape : str
            The shape of the photometric aperture. Can be either square or circle
        contained_energy : Union[str, int, float]
            The energy contained within the photometric aperture.
        contained_pixels : u.Quantity
            The pixels contained within the photometric aperture.
        """
        super().__init__(parent)
        if type(quantum_efficiency) == str:
            self.__quantum_efficiency = SpectralQty.fromFile(quantum_efficiency, u.nm, u.electron / u.photon)
        else:
            self.__quantum_efficiency = quantum_efficiency
        self.__pixel_geometry = pixel_geometry
        self.__pixel_size = pixel_size
        self.__read_noise = read_noise
        self.__dark_current = dark_current
        self.__well_capacity = well_capacity
        self.__f_number = f_number
        self.__center_offset = center_offset
        self.__shape = shape
        self.__contained_energy = contained_energy
        self.__contained_pixels = contained_pixels
        self.__common_conf = common_conf
        # Calculate central wavelength
        self.__central_wl = self.__common_conf.wl_min() + (
                self.__common_conf.wl_max() - self.__common_conf.wl_min()) / 2
        # Parse PSF
        if hasattr(common_conf, "psf") and common_conf.psf().lower() == "airy":
            # Use an airy disk as PSF
            self.__psf = Airy(self.__f_number, self.__central_wl, common_conf.d_aperture(), common_conf.psf.osf,
                              pixel_size)
        else:
            # Read PSF from Zemax file
            self.__psf = Zemax(common_conf.psf(), self.__f_number, self.__central_wl, common_conf.d_aperture(),
                               common_conf.psf.osf, pixel_size)

    @u.quantity_input(exp_time="time")
    def getSNR(self, exp_time: u.Quantity) -> u.dimensionless_unscaled:
        """
        Calculate the signal to background ratio (SNR) for the given exposure time using the CCD-equation.

        Parameters
        ----------
        exp_time : time-Quantity
            The exposure time to calculate the SNR for.

        Returns
        -------
        snr : Quantity
            The calculated SNR as dimensionless quantity
        """
        # Calculate the electron currents
        signal_current, background_current, read_noise, dark_current = self.__exposePixels()
        # Calculate the SNR using the CCD-equation
        getLogger("root").info("Calculating the SNR...", extra={"user_waiting": True})
        snr = signal_current.sum() * exp_time / np.sqrt(
            (signal_current + background_current + dark_current).sum() * exp_time + (read_noise ** 2).sum())
        # Print information
        if exp_time.size > 1:
            pbar = enlighten.get_manager().counter(**dict(total=len(exp_time), desc='SNR', unit='configurations'))
            for exp_time_ in pbar(exp_time):
                self.__printDetails(signal_current * exp_time_, background_current * exp_time_, read_noise,
                                    dark_current * exp_time_, "t_exp=%.2f s: " % exp_time_.value)
        else:
            self.__printDetails(signal_current * exp_time, background_current * exp_time, read_noise,
                                dark_current * exp_time, "t_exp=%.2f s: " % exp_time.value)
        # Return the value of the SNR, ignoring the physical units (electrons^0.5)
        return snr.value * u.dimensionless_unscaled

    @u.quantity_input(snr=u.dimensionless_unscaled)
    def getExpTime(self, snr: u.Quantity) -> u.s:
        """
        Calculate the necessary exposure time in order to achieve the given SNR.

        Parameters
        ----------
        snr : Quantity
            The SNR for which the necessary exposure time shall be calculated as dimensionless quantity.

        Returns
        -------
        exp_time : Quantity
            The necessary exposure time in seconds.
        """
        # Calculate the electron currents
        signal_current, background_current, read_noise, dark_current = self.__exposePixels()
        # Calculate the electron currents for all pixels
        signal_current_tot = signal_current.sum()
        # Fix the physical units of the SNR
        snr = snr * u.electron ** 0.5

        # Calculate the ratio of the background- and dark-current to the signal current as auxiliary variable
        current_ratio = (background_current.sum() + dark_current.sum()) / signal_current_tot
        # Calculate the necessary exposure time as inverse of the CCD-equation
        exp_time = snr ** 2 * (
                1 + current_ratio + np.sqrt((1 + current_ratio) ** 2 + 4 * (read_noise ** 2).sum() / snr ** 2)) / (
                           2 * signal_current_tot)
        # Print information
        if exp_time.size > 1:
            pbar = enlighten.get_manager().counter(**dict(total=len(exp_time), desc='Exposure Time',
                                                          unit='configurations'))
            for snr_, exp_time_ in pbar(zip(snr, exp_time)):
                self.__printDetails(signal_current * exp_time_, background_current * exp_time_, read_noise,
                                    dark_current * exp_time_, "SNR=%.2f: " % snr_.value)
        else:
            self.__printDetails(signal_current * exp_time, background_current * exp_time, read_noise,
                                dark_current * exp_time, "SNR=%.2f: " % snr.value)
        return exp_time

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
        # Calculate the electron currents
        signal_current, background_current, read_noise, dark_current = self.__exposePixels()
        # Fix the physical units of the SNR
        snr = snr * u.electron ** 0.5
        signal_current_lim = snr * (snr + np.sqrt(
            snr ** 2 + 4 * (exp_time * (background_current.sum() + dark_current.sum()) +
                            (read_noise ** 2).sum()))) / (2 * exp_time)
        # Print information
        if exp_time.size > 1:
            pbar = enlighten.get_manager().counter(**dict(total=len(exp_time), desc='Sensitivity',
                                                          unit='configurations'))
            for snr_, exp_time_, signal_current_lim_ in pbar(zip(snr, exp_time, signal_current_lim)):
                self.__printDetails(signal_current_lim_ * exp_time_, background_current * exp_time_, read_noise,
                                    dark_current * exp_time_,
                                    "SNR=%.2f t_exp=%.2f s: " % (snr_.value, exp_time_.value))
        else:
            self.__printDetails(signal_current_lim * exp_time, background_current * exp_time, read_noise,
                                dark_current * exp_time,
                                "SNR=%.2f t_exp=%.2f s: " % (snr.value, exp_time.value))
        return target_brightness - 2.5 * np.log10(signal_current_lim / signal_current.sum()) * u.mag

    @u.quantity_input(signal=u.electron, background=u.electron, read_noise=u.electron ** 0.5, dark=u.electron)
    def __printDetails(self, signal: u.Quantity, background: u.Quantity, read_noise: u.Quantity,
                       dark: u.Quantity, prefix: str = ""):
        """
        Print details on the signal and noise composition.

        Parameters
        ----------
        signal : Quantity
            The collected electrons from the target in electrons.
        background : Quantity
            The collected electrons from the background in electrons.
        read_noise : Quantity
            The read noise in electrons.
        dark : Quantity
            The electrons from the dark current in electrons.

        Returns
        -------
        """
        # Calculate the total collected electrons per pixel
        total = signal + background + dark
        # Check for overexposed pixels
        overexposed = total > self.__well_capacity
        if np.any(overexposed):
            # Show a warning for the overexposed pixels
            warning(prefix + str(np.count_nonzero(overexposed)) + " pixels are overexposed.")
        info("--------------------------------------------------------------------------------------------------------")
        info(prefix + "Collected electrons from target:     %1.2e electrons" % signal.sum().value)
        info(prefix + "Collected electrons from background: %1.2e electrons" % background.sum().value)
        info(prefix + "Electrons from dark current:         %1.2e electrons" % dark.sum().value)
        info(prefix + "Read noise:                          %1.2e electrons" % (read_noise ** 2).sum().value)
        info(prefix + "Total collected electrons:           %1.2e electrons" % total.sum().value)
        info("--------------------------------------------------------------------------------------------------------")

    @u.quantity_input(signal=u.electron, background=u.electron, read_noise=u.electron ** 0.5, dark=u.electron)
    def __output(self, signal: u.Quantity, background: u.Quantity, read_noise: u.Quantity,
                 dark: u.Quantity, prefix: str = ""):
        """
        Write the signal and the noise in electrons to files.

        Parameters
        ----------
        signal : Quantity
            The collected electrons from the target in electrons.
        background : Quantity
            The collected electrons from the background in electrons.
        read_noise : Quantity
            The read noise in electrons.
        dark : Quantity
            The electrons from the dark current in electrons.

        Returns
        -------
        """
        pass

    def __exposePixels(self) -> Tuple[u.Quantity, u.Quantity, u.Quantity, u.Quantity]:
        """
        Expose the pixels and calculate the signal and noise electron currents per pixel.

        Returns
        -------
        signal_current : Quantity
            The electron current from the target as PixelMask in electrons / s
        background_current : Quantity
            The electron current from the background as PixelMask in electrons / s
        read_noise : Quantity
            The read noise per pixel in electrons
        dark_current : Quantity
            The electron current from the dark noise as PixelMask in electrons / s
        """
        # Calculate the total incoming electron current
        getLogger("root").info("Calculating incoming electron current...", extra={"user_waiting": True})
        signal_current, size, obstruction, background_current = self.__calcIncomingElectronCurrent()
        # getLogger("root").info("Finished calculating incoming electron current", extra={"user_waiting": False})
        # Initialize a new PixelMask
        mask = PixelMask(self.__pixel_geometry, self.__pixel_size, self.__center_offset)
        if size.lower() == "extended":
            # Target is extended, a diameter of 0 pixels results in a mask with one pixel marked
            d_photometric_ap = 0 * u.pix
            # Mask the pixels to be exposed
            mask.createPhotometricAperture("circle", d_photometric_ap / 2, np.array([0, 0]) << u.pix)
        else:
            # Target is a point source
            if self.__contained_pixels is not None:
                # Calculate the diameter of the photometric aperture as square root of the contained pixels
                d_photometric_ap = np.sqrt(self.__contained_pixels.value) * u.pix
                # Mask the pixels to be exposed
                mask.createPhotometricAperture("square", d_photometric_ap / 2, np.array([0, 0]) << u.pix)
            else:
                # Calculate the diameter of the photometric aperture from the given contained energy
                getLogger("root").info("Calculating the diameter of the photometric aperture...",
                                       extra={"user_waiting": True})
                d_photometric_ap = self.__calcPhotometricAperture(obstruction)
                # Mask the pixels to be exposed
                mask.createPhotometricAperture(self.__shape, d_photometric_ap / 2)
        # Calculate the background current PixelMask
        background_current = mask * background_current * u.pix
        # Calculate the read noise PixelMask
        read_noise = mask * self.__read_noise * u.pix
        # Calculate the dark current PixelMask
        dark_current = mask * self.__dark_current * u.pix
        if self.__contained_pixels is None and size.lower() != "extended":
            if type(self.__contained_energy) == str:
                if self.__contained_energy.lower() == "peak":
                    info("The radius of the photometric aperture is %.2f pixels. This equals the peak value" % (
                            d_photometric_ap.value / 2))
                elif self.__contained_energy.lower() == "fwhm":
                    info("The radius of the photometric aperture is %.2f pixels. This equals the FWHM" % (
                            d_photometric_ap.value / 2))
                elif self.__contained_energy.lower() == "min":
                    info("The radius of the photometric aperture is %.2f pixels. This equals the first minimum" % (
                            d_photometric_ap.value / 2))
            else:
                info("The radius of the photometric aperture is %.2f pixels. This equals %.0f%% encircled energy" %
                     (d_photometric_ap.value / 2, self.__contained_energy))
        info("The photometric aperture contains " + str(np.count_nonzero(mask)) + " pixels.")
        if size.lower() != "extended":
            # Map the PSF onto the pixel mask in order to get the relative irradiance of each pixel
            getLogger("root").info("Mapping the PSF onto the pixel grid...", extra={"user_waiting": True})
            mask = self.__psf.mapToPixelMask(mask,
                                             getattr(getattr(self.__common_conf, "jitter_sigma", None), "val", None),
                                             obstruction)
        # Calculate the signal current PixelMask
        signal_current = mask * signal_current
        return signal_current, background_current, read_noise, dark_current

    def __calcPhotometricAperture(self, obstruction: float) -> u.Quantity:
        """
        Calculate the diameter of the photometric aperture

        Parameters
        ----------
        obstruction : float
            The obstruction factor as A_ob / A_ap.

        Returns
        -------
        d_photometric_ap : Quantity
            The diameter of the photometric aperture in pixels.
        """
        # Calculate the reduced observation angle
        jitter_sigma = getattr(getattr(self.__common_conf, "jitter_sigma", None), "val", None)
        reduced_observation_angle = self.__psf.calcReducedObservationAngle(self.__contained_energy, jitter_sigma,
                                                                           obstruction)
        debug("Reduced observation angle: %.2f" % reduced_observation_angle.value)
        # Calculate angular width of PSF
        observation_angle = (reduced_observation_angle * self.__central_wl / self.__common_conf.d_aperture() *
                             180.0 / np.pi * 3600).decompose() * u.arcsec
        # Calculate FOV of a single pixel
        pixel_fov = (self.__pixel_size / (self.__f_number * self.__common_conf.d_aperture()) * 180.0 /
                     np.pi * 3600).decompose() * u.arcsec
        # Calculate the radius of the photometric aperture in pixels
        d_photometric_ap = observation_angle / pixel_fov
        return d_photometric_ap * u.pix

    def __calcIncomingElectronCurrent(self) -> Tuple[u.Quantity, str, float, u.Quantity]:
        """
        Calculate the detected electron current of the signal and the background.

        Returns
        -------
        signal_current : Quantity
            The electron current on the detector caused by the target in electrons / s.
        size : str
            The size of the target.
        obstruction : float
            The obstruction factor as A_ob / A_ap.
        background_current : Quantity
            The electron current on the detector caused by the background in electrons / (s * pix).
        """
        # Calculate the photon current of the background
        info("Calculating the background photon current.")
        background_photon_current = self._parent.calcBackground() * np.pi * (
                self.__pixel_size.to(u.m) ** 2 / u.pix) / (4 * self.__f_number ** 2 + 1) * (1 * u.sr)
        # Calculate the incoming photon current of the target
        info("Calculating the signal photon current.")
        signal, size, obstruction = self._parent.calcSignal()
        signal_photon_current = signal * np.pi * (self.__common_conf.d_aperture() / 2) ** 2
        # Calculate the electron current of the background and thereby handling the photon energy as lambda-function
        background_current = (
                background_photon_current / (lambda wl: (const.h * const.c / wl).to(u.W * u.s) / u.photon) *
                self.__quantum_efficiency).integrate()
        # Calculate the electron current of the signal and thereby handling the photon energy as lambda-function
        signal_current = (signal_photon_current / (lambda wl: (const.h * const.c / wl).to(u.W * u.s) / u.photon) *
                          self.__quantum_efficiency).integrate()
        debug("Signal current: %1.2e e-/s" % signal_current.value)
        debug("Target size: " + size)
        debug("Obstruction: %.2f" % obstruction)
        debug("Background current: %1.2e e-/s" % background_current.value)
        return signal_current, size, obstruction, background_current

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
        if not hasattr(sensor, "f_number"):
            return "Missing container 'f_number'."
        mes = sensor.f_number.check_float("val")
        if mes is not None:
            return "f_number: " + mes
        if not hasattr(sensor, "pixel_geometry"):
            return "Missing container 'pixel_geometry'."
        mes = sensor.pixel_geometry.check_quantity("val", u.pix)
        if mes is not None:
            return "pixel_geometry: " + mes
        if hasattr(sensor, "center_offset") and isinstance(sensor.center_offset, Entry):
            mes = sensor.center_offset.check_quantity("val", u.pix)
            if mes is not None:
                return "center_offset: " + mes

        # Check pixel
        if not hasattr(sensor, "pixel"):
            return "Missing container 'pixel'."
        if not hasattr(sensor.pixel, "quantum_efficiency"):
            return "Missing container 'quantum_efficiency'."
        mes = sensor.pixel.quantum_efficiency.check_quantity("val", u.electron / u.photon)
        if mes is not None:
            mes = sensor.pixel.quantum_efficiency.check_file("val")
            if mes is not None:
                return "pixel -> quantum_efficiency: " + mes
        if not hasattr(sensor.pixel, "pixel_size"):
            return "Missing container 'pixel_size'."
        mes = sensor.pixel.pixel_size.check_quantity("val", u.m)
        if mes is not None:
            return "pixel -> pixel_size: " + mes
        if not hasattr(sensor.pixel, "dark_current"):
            return "Missing container 'dark_current'."
        mes = sensor.pixel.dark_current.check_quantity("val", u.electron / (u.pix * u.s))
        if mes is not None:
            return "pixel -> dark_current: " + mes
        if not hasattr(sensor.pixel, "sigma_read_out"):
            return "Missing container 'sigma_read_out'."
        mes = sensor.pixel.sigma_read_out.check_quantity("val", u.electron ** 0.5 / u.pix)
        if mes is not None:
            return "pixel -> sigma_read_out: " + mes
        if not hasattr(sensor.pixel, "well_capacity"):
            return "Missing container 'well_capacity'."
        mes = sensor.pixel.well_capacity.check_quantity("val", u.electron)
        if mes is not None:
            return "pixel -> well_capacity: " + mes

        # Check photometric aperture
        if conf.astroscene.target.size == "point":
            if not hasattr(sensor, "photometric_aperture"):
                return "Missing container 'photometric_aperture'."
            if hasattr(sensor.photometric_aperture, "contained_pixels"):
                mes = sensor.photometric_aperture.contained_pixels.check_quantity("val", u.pix)
                if mes is not None:
                    return "photometric_aperture -> contained_pixels: " + mes
            else:
                if not hasattr(sensor.photometric_aperture, "shape"):
                    return "Missing container 'shape'."
                mes = sensor.photometric_aperture.shape.check_selection("val", ["square", "circle"])
                if mes is not None:
                    return "photometric_aperture -> shape: " + mes
                if not hasattr(sensor.photometric_aperture, "contained_energy"):
                    return "Missing container 'contained_energy'."
                mes = sensor.photometric_aperture.contained_energy.check_float("val")
                if mes is not None:
                    if conf.common.psf().lower() == "airy":
                        mes = sensor.photometric_aperture.contained_energy.check_selection("val",
                                                                                           ["peak", "FWHM", "fwhm",
                                                                                            "min"])
                        if mes is not None:
                            return "photometric_aperture -> contained_energy: " + mes
                    else:
                        mes = sensor.photometric_aperture.contained_energy.check_selection("val", ["FWHM", "fwhm"])
                        if mes is not None:
                            return "photometric_aperture -> contained_energy: " + mes
