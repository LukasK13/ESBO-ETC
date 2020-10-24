from unittest import TestCase
from esbo_etc import ATRAN, FileTarget, SpectralQty
import numpy as np
import astropy.units as u


class TestATRAN(TestCase):
    def setUp(self):
        self.target = FileTarget("tests/data/target/target_demo_3.csv", np.arange(16, 16.1, 0.01) << u.um)
        self.atmosphere = ATRAN(parent=self.target, transmittance="tests/data/atmosphere/atran.dat", temp=240 * u.K)
        self.atmosphere2 = ATRAN(parent=self.target, altitude=15 * u.km, wl_min=16 * u.um, wl_max=16.1 * u.um,
                                 temp=240 * u.K)

    def test_calcSignal(self):
        self.assertEqual(self.atmosphere.calcSignal()[0],
                         SpectralQty(np.arange(16, 16.1, 0.01) << u.um,
                                     np.array([6.555e-16, 1.03e-15, 4.311e-16, 6.13e-16, 1.016e-15, 1.077e-15,
                                               4.733e-16, 8.143e-16, 1.12e-15, 1.128e-15, 5.569e-16]) << u.W / (
                                             u.m ** 2 * u.nm)))
        self.assertEqual(self.atmosphere2.calcSignal()[0],
                         SpectralQty(np.arange(16, 16.1, 0.01) << u.um,
                                     np.array([8.469e-16, 1.068e-15, 5.145e-16, 8.574e-16, 1.087e-15, 1.113e-15,
                                               5.08e-16, 9.303e-16, 1.15e-15, 1.107e-15, 0]) << u.W / (
                                             u.m ** 2 * u.nm)))

    def test_calcBackground(self):
        self.assertTrue(np.allclose(self.atmosphere.calcBackground().qty,
                                    np.array([1.109e-3, 1.97e-4, 1.686e-3, 1.253e-3, 2.989e-4, 1.741e-4, 1.618e-3,
                                              8.301e-4, 1.377e-4, 1.431e-4, 1.46e-3]) << u.W / (
                                            u.m ** 2 * u.nm * u.sr), atol=1e-6))
