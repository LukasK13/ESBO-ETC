from unittest import TestCase
from esbo_etc import CosmicBackground, BlackBodyTarget, SpectralQty
import numpy as np
import astropy.units as u


class TestCosmicBackground(TestCase):
    def setUp(self):
        self.target = BlackBodyTarget(np.arange(100, 105) * u.um, mag=0 * u.mag)
        self.cosmic = CosmicBackground(self.target)

    def test_calcSignal(self):
        self.assertTrue(self.cosmic.calcSignal()[0] == SpectralQty(np.arange(100, 105) * u.um,
                                                                   np.array([6.65e-19, 6.391e-19, 6.145e-19, 5.91e-19,
                                                                             5.687e-19]) << u.W / (u.m ** 2 * u.nm)))

    def test_calcBackground(self):
        self.assertTrue(self.cosmic.calcBackground() == SpectralQty(np.arange(100, 105) * u.um,
                                                                    np.array(
                                                                        [1.398e-28, 2.244e-28, 3.566e-28, 5.614e-28,
                                                                         8.756e-28]) << u.W / (
                                                                            u.m ** 2 * u.nm * u.sr)))
