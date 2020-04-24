from unittest import TestCase
from esbo_etc.classes.target.BlackBodyTarget import BlackBodyTarget
from esbo_etc.classes.SpectralQty import SpectralQty
import numpy as np
import astropy.units as u


class TestBlackBodyTarget(TestCase):
    def setUp(self):
        self.target = BlackBodyTarget(wl_bins=np.arange(400, 800, 100) * u.nm,
                                      temp=5778 * u.K, mag=10 * u.mag, band="U")

    def test_calcSignal(self):
        signal = SpectralQty(np.arange(400, 800, 100) << u.nm, np.array([4.91164694e-15, 5.61732017e-15, 5.22403225e-15,
                                                                         4.43017583e-15]) << u.W / (u.m ** 2 * u.nm))
        self.assertEqual(self.target.calcSignal(), signal)

    def test_calcBackground(self):
        noise = SpectralQty(np.arange(400, 800, 100) << u.nm, np.repeat(0, 4) << u.W / (u.m ** 2 * u.nm * u.sr))
        self.assertEqual(self.target.calcBackground(), noise)
