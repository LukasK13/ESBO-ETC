from unittest import TestCase
from esbo_etc.classes.SpectralQty import SpectralQty
import astropy.units as u
import numpy as np


class TestSpectralQty(TestCase):
    qty = np.arange(1.1e-15, 2.0e-15, 1e-16) << u.W / (u.m ** 2 * u.nm)
    wl = np.arange(200, 210, 1) << u.nm

    def setUp(self):
        self.sqty = SpectralQty(self.wl, self.qty)

    def test_equality(self):
        sqty_2 = SpectralQty(self.wl, self.qty)
        self.assertTrue(self.sqty.__eq__(sqty_2))

    def test_rebinning(self):
        # Test interpolation
        wl_new = np.arange(200.5, 210.5, 1) << u.nm
        sqty_new = SpectralQty(wl_new, [1.15e-15, 1.25e-15, 1.35e-15, 1.45e-15, 1.55e-15, 1.65e-15, 1.75e-15, 1.85e-15,
                                        1.95e-15, 2.05e-15] << u.W / (u.m ** 2 * u.nm))
        self.sqty.rebin(wl_new)
        self.assertTrue(self.sqty.__eq__(sqty_new))

        # Test binning
        self.setUp()
        wl_new = np.arange(200.5, 210, 2) << u.nm
        sqty_new = SpectralQty(wl_new, [1.15e-15, 1.35e-15, 1.55e-15, 1.75e-15, 1.95e-15] << u.W / (u.m ** 2 * u.nm))
        self.sqty.rebin(wl_new)
        self.assertTrue(self.sqty.__eq__(sqty_new))
