from unittest import TestCase
from esbo_etc.classes.target.BlackBodyTarget import BlackBodyTarget
from esbo_etc.classes.SpectralQty import SpectralQty
import numpy as np
import astropy.units as u


class TestBlackBodyTarget(TestCase):
    def setUp(self):
        self.target = BlackBodyTarget(wl_bins=np.arange(400, 800, 100) * u.nm,
                                      temp=5778 * u.K, mag=10 * u.mag, band="U")

    def test_signal(self):
        signal = SpectralQty(np.arange(400, 800, 100) << u.nm,
                             [4.77851291e-15, 5.46505832e-15, 5.08243077e-15,
                              4.31009246e-15] << u.W / (u.m ** 2 * u.nm))
        self.assertTrue(self.target.calcSignal().__eq__(signal))

    def test_noise(self):
        noise = SpectralQty(np.arange(400, 800, 100) << u.nm,
                            [0.] * 10 << u.W / (u.m ** 2 * u.nm * u.sr))
        self.assertEqual(self.target.calcNoise(), noise)
