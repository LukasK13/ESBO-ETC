from unittest import TestCase
from esbo_etc.classes.target.FileTarget import FileTarget
from esbo_etc.classes.SpectralQty import SpectralQty
import astropy.units as u
import numpy as np


class TestFileTarget(TestCase):
    def setUp(self):
        self.target = FileTarget("tests/data/target/target_demo_1.csv", np.arange(200, 210, 1) << u.nm)

    def test_calcSignal(self):
        signal = SpectralQty(np.arange(200, 210, 1) << u.nm,
                             np.arange(1.1e-15, 2.0e-15, 1e-16) << u.W / (u.m ** 2 * u.nm))
        self.assertEqual(self.target.calcSignal(), (signal, 0.0))

    def test_calcBackground(self):
        noise = SpectralQty(np.arange(200, 210, 1) << u.nm,
                            np.repeat(0, 10) << u.W / (u.m ** 2 * u.nm * u.sr))
        self.assertEqual(self.target.calcBackground(), noise)
