from unittest import TestCase
from esbo_etc.classes.target.FileTarget import FileTarget
from esbo_etc.classes.SpectralQty import SpectralQty
import astropy.units as u
import numpy as np


class TestFileTarget(TestCase):
    def setUp(self):
        self.target = FileTarget("data/target/target_demo_1.csv")

    def test_signal(self):
        signal = SpectralQty(np.arange(200, 210, 1) << u.nm,
                             np.arange(1.1e-15, 2.0e-15, 1e-16) << u.W / (u.m ** 2 * u.nm))
        self.assertTrue(self.target.calcSignal().__eq__(signal))

    def test_noise(self):
        noise = SpectralQty(np.arange(200, 210, 1) << u.nm,
                            [0.] * 10 << u.W / (u.m ** 2 * u.nm * u.sr))
        self.assertEqual(self.target.calcNoise(), noise)
