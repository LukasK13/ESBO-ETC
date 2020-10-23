from ..target.ATarget import ATarget
from ..SpectralQty import SpectralQty
import astropy.units as u
from astropy.modeling.models import BlackBody
from astropy.constants import c, k_B
from ...lib.logger import logger
from ..Entry import Entry
from typing import Union
import numpy as np


class BlackBodyTarget(ATarget):
    """
    This class models the spectral flux density of a star of given magnitude using as black body radiator
    """
    # Bands from Handbook of Space Astronomy and Astrophysics p. 139
    _band = dict(U=dict(wl=365 * u.nm, sfd=4.27e-11 * u.W / (u.m ** 2 * u.nm)),
                 B=dict(wl=440 * u.nm, sfd=6.61e-11 * u.W / (u.m ** 2 * u.nm)),
                 V=dict(wl=550 * u.nm, sfd=3.64e-11 * u.W / (u.m ** 2 * u.nm)),
                 R=dict(wl=700 * u.nm, sfd=1.74e-11 * u.W / (u.m ** 2 * u.nm)),
                 I=dict(wl=900 * u.nm, sfd=8.32e-12 * u.W / (u.m ** 2 * u.nm)),
                 J=dict(wl=1250 * u.nm, sfd=3.18e-12 * u.W / (u.m ** 2 * u.nm)),
                 H=dict(wl=1650 * u.nm, sfd=1.18e-12 * u.W / (u.m ** 2 * u.nm)),
                 K=dict(wl=2200 * u.nm, sfd=4.17e-13 * u.W / (u.m ** 2 * u.nm)),
                 L=dict(wl=3600 * u.nm, sfd=6.23e-14 * u.W / (u.m ** 2 * u.nm)),
                 M=dict(wl=4800 * u.nm, sfd=2.07e-14 * u.W / (u.m ** 2 * u.nm)),
                 N=dict(wl=10200 * u.nm, sfd=1.23e-15 * u.W / (u.m ** 2 * u.nm)))

    @u.quantity_input(wl_bins='length', temp=[u.Kelvin, u.Celsius], mag=[u.mag, u.mag / u.sr])
    def __init__(self, wl_bins: u.Quantity, temp: u.Quantity = 5778 * u.K, mag: u.Quantity = None,
                 band: str = "V", law: str = "Planck"):
        """
        Initialize a new black body point source

        Parameters
        ----------
        wl_bins : length-Quantity
            Wavelengths used for binning
        temp : Quantity in Kelvin / Celsius
            Temperature of the black body
        mag : Quantity in mag or mag / sr
            Desired apparent magnitude of the black body source. If the magnitude is given in mag / sr or an equivalent
            unit, an extended source will be assumed.
        band : str
            Band used for fitting the planck curve to a star of 0th magnitude. Can be one of [U, B, V, R, I, J, H, K].
        law : str
            Which law to use for the calculation of the flux values. Can be either 'Planck' for using Planck's law or
            'RJ' to use the Rayleigh-Jeans approximation.

        Returns
        -------
        """
        if band.upper() not in self._band.keys():
            logger.error("Band has to be one of '[" + ", ".join(list(self._band.keys())) + "]'")
        # Create blackbody model with given temperature
        bb = None
        if law.lower() == "planck":
            bb = BlackBody(temperature=temp, scale=1 * u.W / (u.m ** 2 * u.nm * u.sr))
        elif law.upper() == "RJ":
            bb = self.__rayleigh_jeans_factory(temp)
        else:
            logger.error("Unknown law '" + law + "' for target type BlackBody.")
        if mag is not None:
            # Calculate the correction factor for a star of 0th magnitude using the spectral flux density
            # for the central wavelength of the given band
            if mag.unit.is_equivalent(u.mag / u.sr):
                solid_angle_unit = (u.mag / mag.unit)
                mag = mag * solid_angle_unit
                factor = self._band[band.upper()]["sfd"] / (bb(self._band[band.upper()]["wl"]) * (
                        solid_angle_unit.to(u.sr) * u.sr))
            else:
                factor = self._band[band.upper()]["sfd"] / (bb(self._band[band.upper()]["wl"]) * u.sr) * u.sr
            # Calculate spectral flux density for the given wavelengths and scale it for a star of the given magnitude
            sfd = bb(wl_bins) * factor * 10 ** (- 2 / 5 * mag / u.mag)  # / 1.195 * 1.16 #  scaling for AETC validation
            wl_bins_2 = np.arange(15.71, 23.71, 0.01) << u.um
            sfd_2 = bb(wl_bins_2) * factor * 10 ** (- 2 / 5 * mag / u.mag)
            sqty_2 = SpectralQty(wl_bins_2, sfd_2).integrate()
            print((sqty_2 / (8 * u.um)).to(u.W / (u.m ** 2 * u.um)))
        else:
            sfd = bb(wl_bins)
        # Initialize super class
        super().__init__(SpectralQty(wl_bins, sfd), wl_bins)

    @staticmethod
    @u.quantity_input(temp=[u.Kelvin, u.Celsius])
    def __rayleigh_jeans_factory(temp: u.Quantity):
        """
        Create a lambda function for the Rayleigh-Jeans law

        Parameters
        ----------
        temp : u.Quantity
            The temperature in Kelvins

        Returns
        -------
        res : lambda
            A lambda function for the Rayleigh-Jeans law with the variable lambda wavelength
        """
        return lambda wl: (2 * c * k_B * temp / wl ** 4 / u.sr).to(u.W / (u.m ** 2 * u.nm * u.sr))

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
        mes = conf.check_quantity("temp", u.K)
        if mes is not None:
            return mes
        if hasattr(conf, "mag"):
            mes = conf.check_quantity("mag", u.mag)
            if mes is not None:
                mes = conf.check_quantity("mag", u.mag / u.sr)
                if mes is not None:
                    return mes
            mes = conf.check_selection("band", ["U", "B", "V", "R", "I", "J", "H", "K", "L", "M", "N"])
            if mes is not None:
                return mes
        if hasattr(conf, "law"):
            mes = conf.check_selection("law", ["Planck", "RJ"])
            if mes is not None:
                return mes
