from unittest import TestCase
from esbo_etc import Atmosphere, FileTarget, SpectralQty
import numpy as np
import astropy.units as u


class TestAtmosphere(TestCase):
    def setUp(self):
        self.target = FileTarget("tests/data/target/target_demo_1.csv", np.arange(200, 208) << u.nm)
        self.atmosphere = Atmosphere(self.target, "tests/data/atmosphere/atmosphere_transmittance_1.csv",
                                     "tests/data/atmosphere/atmosphere_emission_1.csv")

    def test_calcSignal(self):
        self.assertEqual(self.atmosphere.calcSignal()[0],
                         SpectralQty(np.arange(200, 208) << u.nm,
                                     np.array([1.10e-15, 1.20e-15, 1.30e-15, 1.26e-15, 1.20e-15, 1.12e-15, 1.02e-15,
                                               0.9e-15]) << u.W / (u.m ** 2 * u.nm)))

    def test_calcBackgrounde(self):
        self.assertEqual(self.atmosphere.calcBackground(),
                         SpectralQty(np.arange(200, 208) << u.nm,
                                     np.array([1.1e-16, 1.2e-16, 1.3e-16, 1.4e-16, 1.5e-16, 1.6e-16, 1.7e-16,
                                               1.8e-16]) << u.W / (u.m ** 2 * u.nm * u.sr)))
