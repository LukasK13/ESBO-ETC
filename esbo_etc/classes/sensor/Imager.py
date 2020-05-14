from astropy import units as u
from .ASensor import ASensor
from ..IRadiant import IRadiant
from ..Entry import Entry
import numpy as np
from typing import Union
from ..psf.Airy import Airy
from ..psf.Zemax import Zemax
from ..SpectralQty import SpectralQty
from .PixelMask import PixelMask
import astropy.constants as const
from logging import info


class Imager(ASensor):
    """
    A class for modelling a Image-sensor
    """
    __encircled_energy: Union[str, float, u.Quantity]

    @u.quantity_input(pixel_size="length", read_noise=u.electron ** 0.5 / u.pix, center_offset=u.pix,
                      dark_current=u.electron / u.pix / u.second, pixel_geometry=u.pix)
    def __init__(self, parent: IRadiant, quantum_efficiency: Union[str, u.Quantity],
                 pixel_geometry: u.Quantity, pixel_size: u.Quantity, read_noise: u.Quantity, dark_current: u.Quantity,
                 f_number: Union[int, float], common_conf: Entry, center_offset: u.Quantity = np.array([0, 0]) << u.nm,
                 shape: str = None, contained_energy: Union[str, int, float] = "FWHM",
                 contained_pixels: u.Quantity = None):
        """
        Initialize a new Image-sensor model.
        Initialize a new Image-sensor model.

        Parameters
        ----------
        parent : IRadiant
            The parent element of the optical component from which the electromagnetic radiation is received.
        quantum_efficiency : Union[str, u.Quantity]
            The quantum efficiency of the detector. This can be either the path to the file containing the values of
            the spectral quantum efficiency or the overall quantum efficiency as int, float or astropy quantity.
        pixel_geometry : u.Quantity
            The geometry of the pixel array as Quantity in pixels with two entries:
            [number of pixels in x-direction, number of pixels in y-direction]
        pixel_size : length-Quantity
            The edge length of a pixel (assumed to be square).
        read_noise : Quantity
            The RMS-read noise per detector pixel in electrons^0.5 / pixel.
        dark_current : Quantity
            The dark current of a detector pixel in electrons / (pixels * s).
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
        if type(quantum_efficiency == str):
            self.__quantum_efficiency = SpectralQty.fromFile(quantum_efficiency, u.nm, u.electron / u.photon)
        elif type(quantum_efficiency) == u.Quantity:
            self.__quantum_efficiency = quantum_efficiency
        self.__pixel_geometry = pixel_geometry
        self.__array = np.zeros((int(pixel_geometry.value[0]), int(pixel_geometry.value[1])))
        self.__pixel_size = pixel_size
        self.__read_noise = read_noise
        self.__dark_current = dark_current
        self.__f_number = f_number
        self.__center_offset = center_offset
        self.__shape = shape
        self.__contained_energy = contained_energy
        if contained_pixels:
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
    def getSNR(self, exp_time: u.Quantity):
        """
        Calculate the signal to background ratio (SNR) for the given exposure time using the CCD-equation.

        Parameters
        ----------
        exp_time : time-Quantity
            The exposure time to calculate the SNR for.

        Returns
        -------
        snr : float
            The calculated SNR
        """

        snr = self.__calcSNR(*self.__exposePixels(), exp_time)
        return snr.value

    def getExpTime(self, snr: float) -> u.Quantity:
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
        # # Calculate the number of exposed pixels which will be used for calculating the noise
        # n_pix_exposed = self.__calcExposedPixels()
        # # Calculate the electron current from the target and the background
        # signal_current, background_current = self.__calcElectronCurrent(n_pix_exposed)
        # # Fix the physical units of the SNR
        # snr = snr * u.electron**0.5
        #
        # # Calculate the ratio of the background- and dark-current to the signal current as auxiliary variable
        # current_ratio = (background_current + n_pix_exposed * self.__dark_current) / signal_current
        # # Calculate the necessary exposure time as inverse of the CCD-equation
        # exp_time = snr ** 2 * (1 + current_ratio + np.sqrt(
        #     (1 + current_ratio) ** 2 + 4 * (self.__read_noise * n_pix_exposed) ** 2 / snr ** 2)) /\
        #     (2 * signal_current)
        # return exp_time

    @u.quantity_input(signal_current=u.electron / u.s, background_current=u.electron / u.s,
                      read_noise=u.electron ** 0.5, dark_current=u.electron / u.s, exp_time="time")
    def __calcSNR(self, signal_current: u.Quantity, background_current: u.Quantity, read_noise: u.Quantity,
                  dark_current: u.Quantity, exp_time: u.Quantity) -> u.dimensionless_unscaled:
        # Calculate the SNR using the CCD-equation
        snr = signal_current.sum() * exp_time / np.sqrt(
            exp_time * (signal_current.sum() + background_current.sum() + dark_current.sum()) + read_noise.sum() ** 2)
        # Return the value of the SNR, ignoring the physical units (electrons^0.5)
        return snr.value * u.dimensionless_unscaled

    def __exposePixels(self) -> (u.electron / u.s, u.electron / u.s, u.electron, u.electron / u.s):
        signal_current, size, obstruction, background_current = self.__calcPixelElectronCurrent()
        mask = PixelMask(self.__pixel_geometry, self.__pixel_size, self.__center_offset)
        if size.lower() == "extended":
            d_photometric_ap = 0 * u.pix
            mask.createPhotometricAperture("circle", d_photometric_ap / 2, np.array([0, 0]) << u.pix)
        else:
            if hasattr(self, "__contained_pixels"):
                d_photometric_ap = np.sqrt(self.__contained_pixels.value) * u.pix
                mask.createPhotometricAperture("square", d_photometric_ap / 2, np.array([0, 0]) << u.pix)
            else:
                d_photometric_ap = self.__calcPhotometricAperture(obstruction)
                mask.createPhotometricAperture(self.__shape, d_photometric_ap / 2)
        background = mask * background_current * u.pix
        read_noise = mask * self.__read_noise * u.pix
        dark_current = mask * self.__dark_current * u.pix
        info("The radius of the photometric aperture is %.2f pixels." % (d_photometric_ap.value / 2))
        info("The photometric aperture contains " + str(np.count_nonzero(mask)) + " pixels.")
        if size.lower() != "extended":
            mask = self.__psf.mapToPixelMask(mask,
                                             getattr(getattr(self.__common_conf, "jitter_sigma", None), "val", None),
                                             obstruction)
        signal = mask * signal_current
        return signal, background, read_noise, dark_current

    def __calcPhotometricAperture(self, obstruction: float) -> u.Quantity:
        # Calculate the reduced observation angle
        # jitter_sigma = self.__common_conf.jitter_sigma() if hasattr(self.__common_conf, "jitter_sigma") else None
        jitter_sigma = getattr(getattr(self.__common_conf, "jitter_sigma", None), "val", None)
        reduced_observation_angle = self.__psf.calcReducedObservationAngle(self.__contained_energy, jitter_sigma,
                                                                           obstruction)

        # Calculate angular width of PSF
        observation_angle = (reduced_observation_angle * self.__central_wl / self.__common_conf.d_aperture() *
                             180.0 / np.pi * 3600).decompose() * u.arcsec
        # Calculate FOV of a single pixel
        pixel_fov = (self.__pixel_size / (self.__f_number * self.__common_conf.d_aperture()) * 180.0 /
                     np.pi * 3600).decompose() * u.arcsec
        # Calculate the radius of the photometric aperture in pixels
        d_photometric_ap = observation_angle / pixel_fov
        return d_photometric_ap * u.pix

    def __calcPixelElectronCurrent(self) -> (u.electron / u.s, str, float, u.electron / (u.pix * u.s)):
        """
        Calculate the detected electron current of the signal and the background.

        Returns
        -------
        signal_current : Quantity
            The electron current on the detector caused by the target in electrons / s.
        size : str
            The size of the target.
        obstruction : float
            The obstruction factor.
        background_current : Quantity
            The electron current on the detector caused by the background in electrons / (s * pix).
        """
        # Calculate the photon current of the background
        background_photon_current = self._parent.calcBackground() * np.pi * (
                self.__pixel_size.to(u.m) ** 2 / u.pix) / (4 * self.__f_number ** 2 + 1) * (1 * u.sr)
        # Calculate the incoming photon current of the target
        signal, size, obstruction = self._parent.calcSignal()
        signal_photon_current = signal * np.pi * self.__common_conf.d_aperture() ** 2
        # Calculate the electron current of the background and thereby handling the photon energy as lambda-function
        background_current = (
                background_photon_current / (lambda wl: (const.h * const.c / wl).to(u.W * u.s) / u.photon) *
                self.__quantum_efficiency).integrate()
        # Calculate the electron current of the signal and thereby handling the photon energy as lambda-function
        signal_current = (signal_photon_current / (lambda wl: (const.h * const.c / wl).to(u.W * u.s) / u.photon) *
                          self.__quantum_efficiency).integrate()
        return signal_current, size, obstruction, background_current

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
            The error message of the check. This will be None if the check was successful.
        """
        if not hasattr(conf, "f_number"):
            return "Missing container 'f_number'."
        mes = conf.f_number.check_float("val")
        if mes is not None:
            return "f_number: " + mes
        if not hasattr(conf, "pixel_geometry"):
            return "Missing container 'pixel_geometry'."
        mes = conf.pixel_geometry.check_quantity("val", u.pix)
        if mes is not None:
            return "pixel_geometry: " + mes
        if hasattr(conf, "center_offset") and isinstance(conf.center_offset, Entry):
            mes = conf.center_offset.check_quantity("val", u.pix)
            if mes is not None:
                return "center_offset: " + mes

        # Check pixel
        if not hasattr(conf, "pixel"):
            return "Missing container 'pixel'."
        if not hasattr(conf.pixel, "quantum_efficiency"):
            return "Missing container 'quantum_efficiency'."
        mes = conf.pixel.quantum_efficiency.check_float("val")
        if mes is not None:
            mes = conf.pixel.quantum_efficiency.check_file("val")
            if mes is not None:
                return "pixel -> quantum_efficiency: " + mes
        if not hasattr(conf.pixel, "pixel_size"):
            return "Missing container 'pixel_size'."
        mes = conf.pixel.pixel_size.check_quantity("val", u.m)
        if mes is not None:
            return "pixel -> pixel_size: " + mes
        if not hasattr(conf.pixel, "dark_current"):
            return "Missing container 'dark_current'."
        mes = conf.pixel.dark_current.check_quantity("val", u.electron / (u.pix * u.s))
        if mes is not None:
            return "pixel -> dark_current: " + mes
        if not hasattr(conf.pixel, "sigma_read_out"):
            return "Missing container 'sigma_read_out'."
        mes = conf.pixel.sigma_read_out.check_quantity("val", u.electron ** 0.5 / u.pix)
        if mes is not None:
            return "pixel -> sigma_read_out: " + mes

        # Check photometric aperture
        if not hasattr(conf, "photometric_aperture"):
            return "Missing container 'photometric_aperture'."
        if hasattr(conf.photometric_aperture, "shape"):
            mes = conf.photometric_aperture.shape.check_selection("val", ["square", "circle"])
            if mes is not None:
                return "photometric_aperture -> shape: " + mes
        if hasattr(conf.photometric_aperture, "contained_energy"):
            mes = conf.photometric_aperture.contained_energy.check_float("val")
            if mes is not None:
                mes = conf.photometric_aperture.contained_energy.check_selection("val", ["peak", "FWHM", "fwhm", "min"])
                if mes is not None:
                    return "photometric_aperture -> contained_energy: " + mes
        if hasattr(conf.photometric_aperture, "contained_pixels"):
            mes = conf.photometric_aperture.contained_pixels.check_quantity("val", u.pix)
            if mes is not None:
                return "photometric_aperture -> contained_pixels: " + mes
