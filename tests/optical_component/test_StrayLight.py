from unittest import TestCase
from esbo_etc import StrayLight, FileTarget, SpectralQty
import numpy as np
import astropy.units as u


class TestStrayLight(TestCase):
    def setUp(self):
        self.target = FileTarget("tests/data/target/target_demo_1.csv", np.arange(200, 210) << u.nm)
        self.zodiac = StrayLight(self.target, "tests/data/straylight/zodiacal_emission_1.csv")

    def test_calcSignal(self):
        self.assertEqual(self.zodiac.calcSignal()[0],
                         SpectralQty(np.arange(200, 210) << u.nm, np.array([1.1e-15, 1.2e-15, 1.3e-15, 1.4e-15, 1.5e-15,
                                                                            1.6e-15, 1.7e-15, 1.8e-15, 1.9e-15,
                                                                            2.0e-15]) << u.W / (u.m ** 2 * u.nm)))

    def test_calcBackground(self):
        self.assertEqual(self.zodiac.calcBackground(),
                         SpectralQty(np.arange(200, 210) << u.nm, np.array([1.1e-16, 1.2e-16, 1.3e-16, 1.4e-16, 1.5e-16,
                                                                            1.6e-16, 1.7e-16, 1.8e-16, 1.9e-16,
                                                                            2.0e-16]) << u.W /
                                     (u.m ** 2 * u.nm * u.sr)))
