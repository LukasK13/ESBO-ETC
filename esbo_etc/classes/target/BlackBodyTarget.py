from ..target.ATarget import ATarget
from ..SpectralQty import SpectralQty
import astropy.units as u
from astropy.modeling.models import BlackBody
from ...lib.helpers import error


class BlackBodyTarget(ATarget):
    """
    This class models the spectral flux density of a star of given magnitude using as black body radiator
    """
    # Bands from Handbook of Space Astronomy and Astrophysics
    # band_sfd = {"U": 1790*u.Jansky, "B": 4063*u.Jansky, "V": 3636*u.Jansky, "R": 3064*u.Jansky,
    #            "I": 2416*u.Jansky, "J": 1590*u.Jansky, "H": 1020*u.Jansky, "K": 640*u.Jansky}
    _band = dict(U=dict(wl=366 * u.nm, sfd=4.175e-11 * u.W / (u.m ** 2 * u.nm)),
                 B=dict(wl=438 * u.nm, sfd=6.32e-11 * u.W / (u.m ** 2 * u.nm)),
                 V=dict(wl=545 * u.nm, sfd=3.631e-11 * u.W / (u.m ** 2 * u.nm)),
                 R=dict(wl=641 * u.nm, sfd=2.177e-11 * u.W / (u.m ** 2 * u.nm)),
                 I=dict(wl=798 * u.nm, sfd=1.126e-11 * u.W / (u.m ** 2 * u.nm)),
                 J=dict(wl=1220 * u.nm, sfd=3.15e-12 * u.W / (u.m ** 2 * u.nm)),
                 H=dict(wl=1630 * u.nm, sfd=1.14e-12 * u.W / (u.m ** 2 * u.nm)),
                 K=dict(wl=2190 * u.nm, sfd=3.96e-13 * u.W / (u.m ** 2 * u.nm)))

    @u.quantity_input(wl_bins='length', temp=[u.Kelvin, u.Celsius], mag=u.mag)
    def __init__(self, wl_bins: u.Quantity, temp: u.Quantity = 5778 * u.K,
                 mag: u.Quantity = 0 * u.mag, band: str = "V"):
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
        super().__init__(SpectralQty(wl_bins, sfd))
