from ..target.ATarget import ATarget
from ..SpectralQty import SpectralQty
import astropy.units as u
from astropy.modeling.models import BlackBody
from ...lib.helpers import error


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
                 L=dict(wl=3600 * u.nm, sfd=4.17e-13 * u.W / (u.m ** 2 * u.nm)),
                 M=dict(wl=4800 * u.nm, sfd=4.17e-13 * u.W / (u.m ** 2 * u.nm)),
                 N=dict(wl=10200 * u.nm, sfd=4.17e-13 * u.W / (u.m ** 2 * u.nm)))

    @u.quantity_input(wl_bins='length', temp=[u.Kelvin, u.Celsius], mag=u.mag)
    def __init__(self, wl_bins: u.Quantity, temp: u.Quantity = 5778 * u.K,
                 mag: u.Quantity = 0 * u.mag, band: str = "V", size: str = "Point"):
        """
        Initialize a new black body point source

        Parameters
        ----------
        wl_bins : length-Quantity
            Wavelengths used for binning
        temp : Quantity in Kelvin / Celsius
            Temperature of the black body
        mag : Quantity in mag
            Desired apparent magnitude of the point source
        band : str
            Band used for fitting the planck curve to a star of 0th magnitude. Can be one of [U, B, V, R, I, J, H, K].
        size : str
            The size of the target. Can be either point or extended

        Returns
        -------
        """
        if band not in self._band.keys():
            error("Band has to be one of '[" + ", ".join(list(self._band.keys())) + "]'")
        # Create blackbody model with given temperature
        bb = BlackBody(temperature=temp, scale=1 * u.W / (u.m ** 2 * u.nm * u.sr))

        # Calculate the correction factor for a star of 0th magnitude using the spectral flux density
        # for the central wavelength of the given band
        factor = self._band[band]["sfd"] / (bb(self._band[band]["wl"]) * u.sr) * u.sr
        # Calculate spectral flux density for the given wavelengths and scale it for a star of the given magnitude
        sfd = bb(wl_bins) * factor * 10 ** (- 2 / 5 * mag / u.mag)

        # Initialize super class
        super().__init__(SpectralQty(wl_bins, sfd), wl_bins, size)
