from unittest import TestCase
from esbo_etc import Filter, BlackBodyTarget, FileTarget, SpectralQty
import numpy as np
import astropy.units as u


class TestFilter(TestCase):
    def test_fromBand(self):
        wl = [400, 500, 501, 545, 589, 590, 600] << u.nm
        target = BlackBodyTarget(wl, temp=5778 * u.K, mag=10 * u.mag, band="U")
        filt = Filter.fromBand(target, "V")
        self.assertEqual(filt.calcSignal(), SpectralQty(wl, [0.0, 0.0, 5.46516556e-15, 5.37748512e-15, 5.15313966e-15,
                                                             0.0, 0.0] << u.W / (u.m ** 2 * u.nm)))

    def test_fromFile(self):
        target = FileTarget("../data/target/target_demo_1.csv")
        filt = Filter.fromFile(target, "data/filter/filter_transmittance.csv")
        self.assertEqual(filt.calcSignal(), SpectralQty(np.arange(200, 210, 1) << u.nm,
                                                        [1.10e-15, 1.20e-15, 1.30e-15, 1.40e-15, 1.35e-15, 1.44e-15,
                                                         1.53e-15, 1.44e-15, 1.52e-15, 1.40e-15] << u.W / (
                                                                    u.m ** 2 * u.nm)))
