from unittest import TestCase
from esbo_etc.classes.SpectralQty import SpectralQty
import astropy.units as u
import numpy as np


class TestSpectralQty(TestCase):
    qty = np.arange(1.1, 1.5, 0.1) << u.W / (u.m ** 2 * u.nm)
    wl = np.arange(200, 204, 1) << u.nm

    def setUp(self):
        self.sqty = SpectralQty(self.wl, self.qty)

    def test___eq__(self):
        sqty_2 = SpectralQty(self.wl, self.qty)
        self.assertEqual(self.sqty, sqty_2)

    def test___mul__(self):
        # Integer
        self.assertEqual(self.sqty * 2, SpectralQty(np.arange(200, 204, 1) << u.nm,
                                                    np.arange(2.2, 3.0, 2e-1) << u.W / (u.m ** 2 * u.nm)))
        self.assertEqual(2 * self.sqty, SpectralQty(np.arange(200, 204, 1) << u.nm,
                                                    np.arange(2.2, 3.0, 2e-1) << u.W / (u.m ** 2 * u.nm)))
        # Float
        self.assertEqual(self.sqty * 2., SpectralQty(np.arange(200, 204, 1) << u.nm,
                                                     np.arange(2.2, 3.0, 2e-1) << u.W / (u.m ** 2 * u.nm)))
        self.assertEqual(2. * self.sqty, SpectralQty(np.arange(200, 204, 1) << u.nm,
                                                     np.arange(2.2, 3.0, 2e-1) << u.W / (u.m ** 2 * u.nm)))
        # SpectralQty
        self.assertEqual(self.sqty * SpectralQty(self.wl, np.arange(1, 5, 1) << u.m),
                         SpectralQty(self.wl, [1.1, 2.4, 3.9, 5.6] << u.W / (u.m * u.nm)))
        self.assertEqual(SpectralQty(self.wl, np.arange(1, 5, 1) << u.m) * self.sqty,
                         SpectralQty(self.wl, [1.1, 2.4, 3.9, 5.6] << u.W / (u.m * u.nm)))
        # rebin without extrapolation and without reduction
        self.assertEqual(
            self.sqty * SpectralQty(np.arange(199.5, 204.5, 1) << u.nm, np.arange(1, 6, 1) << u.m),
            SpectralQty(self.wl, [1.65, 3.0, 4.55, 6.3] * u.W / (u.m * u.nm)))
        # rebin without extrapolation and with reduction
        self.assertEqual(
            self.sqty * SpectralQty(np.arange(200.5, 204.5, 1) << u.nm, np.arange(1, 5, 1) << u.m),
            SpectralQty(range(201, 204) << u.nm, [1.8, 3.25, 4.9] << u.W / (u.m * u.nm)))

    def test___sub__(self):
        # Quantity
        self.assertEqual(self.sqty - 0.1 * u.W / (u.m ** 2 * u.nm),
                         SpectralQty(np.arange(200, 204, 1) << u.nm,
                                     np.arange(1.0, 1.4, 0.1) << u.W / (u.m ** 2 * u.nm)))
        # SpectralQty
        self.assertEqual(
            self.sqty - SpectralQty(np.arange(200, 204, 1) << u.nm, np.arange(1, 5, 1) << u.W / (u.m ** 2 * u.nm)),
            SpectralQty(self.wl, [0.1, -0.8, -1.7, -2.6] * u.W / (u.m ** 2 * u.nm)))
        # rebin without extrapolation and without reduction
        self.assertEqual(
            self.sqty - SpectralQty(np.arange(199.5, 204.5, 1) << u.nm, np.arange(1, 6, 1) << u.W / (u.m ** 2 * u.nm)),
            SpectralQty(self.wl, [-0.4, -1.3, -2.2, -3.1] * u.W / (u.m ** 2 * u.nm)))
        # rebin without extrapolation and with reduction
        self.assertEqual(
            self.sqty - SpectralQty(np.arange(200.5, 204.5, 1) << u.nm, np.arange(1, 5, 1) << u.W / (u.m ** 2 * u.nm)),
            SpectralQty(range(201, 204) << u.nm, [-0.3, -1.2, -2.1] << u.W / (u.m ** 2 * u.nm)))

    def test___add__(self):
        # Quantity
        self.assertEqual(self.sqty + 1.0 * u.W / (u.m ** 2 * u.nm),
                         SpectralQty(np.arange(200, 204, 1) << u.nm,
                                     np.arange(2.1, 2.5, 0.1) << u.W / (u.m ** 2 * u.nm)))
        # SpectralQty
        self.assertEqual(
            self.sqty + SpectralQty(np.arange(200, 204, 1) << u.nm, np.arange(1, 5, 1) << u.W / (u.m ** 2 * u.nm)),
            SpectralQty(self.wl, [2.1, 3.2, 4.3, 5.4] * u.W / (u.m ** 2 * u.nm)))
        # rebin without extrapolation and without reduction
        self.assertEqual(
            self.sqty + SpectralQty(np.arange(199.5, 204.5, 1) << u.nm, np.arange(1, 6, 1) << u.W / (u.m ** 2 * u.nm)),
            SpectralQty(self.wl, [2.6, 3.7, 4.8, 5.9] * u.W / (u.m ** 2 * u.nm)))
        # rebin without extrapolation and with reduction
        self.assertEqual(
            self.sqty + SpectralQty(np.arange(200.5, 204.5, 1) << u.nm, np.arange(1, 5, 1) << u.W / (u.m ** 2 * u.nm)),
            SpectralQty(range(201, 204) << u.nm, [2.7, 3.8, 4.9] << u.W / (u.m ** 2 * u.nm)))
        # lambda
        sqty_2 = lambda wl: 1 * u.W / (u.m ** 2 * u.nm ** 2) * wl
        self.assertEqual(self.sqty + sqty_2,
                         SpectralQty(self.wl, [201.1, 202.2, 203.3, 204.4] << u.W / (u.m**2 * u.nm)))

    def test_rebinning(self):
        # Test interpolation
        wl_new = np.arange(200.5, 210.5, 1) << u.nm
        sqty_res = SpectralQty(wl_new[:3], [1.15, 1.25, 1.35] << u.W / (u.m ** 2 * u.nm))
        sqty_rebin = self.sqty.rebin(wl_new)
        self.assertEqual(sqty_rebin, sqty_res)

        # Test extrapolation
        wl_new = np.arange(200.5, 210.5, 1) << u.nm
        sqty_res = SpectralQty(wl_new, [1.15, 1.25, 1.35, 1.45, 1.55, 1.65, 1.75, 1.85,
                                        1.95, 2.05] << u.W / (u.m ** 2 * u.nm))
        sqty_extrapol = SpectralQty(self.wl, self.qty, extrapolate=True)
        sqty_rebin = sqty_extrapol.rebin(wl_new)
        self.assertEqual(sqty_rebin, sqty_res)

        # Test binning
        self.setUp()
        wl_new = np.arange(200.5, 210, 2) << u.nm
        sqty_res = SpectralQty(wl_new[:2], [1.15, 1.35] << u.W / (u.m ** 2 * u.nm))
        sqty_rebin = self.sqty.rebin(wl_new)
        self.assertEqual(sqty_rebin, sqty_res)

    def test_fromFile(self):
        sqty = SpectralQty.fromFile("data/target/target_demo_1.csv", u.nm, u.W / (u.m ** 2 * u.nm))
        res = SpectralQty(np.arange(1.1, 2.1, 0.1) * 1e-15 << u.W / (u.m**2 * u.nm),
                                           np.arange(200, 210, 1) << u.nm)
        self.assertEqual(sqty, SpectralQty(np.arange(200, 210, 1) << u.nm,
                                           np.arange(1.1, 2.1, 0.1) * 1e-15 << u.W / (u.m**2 * u.nm)))
