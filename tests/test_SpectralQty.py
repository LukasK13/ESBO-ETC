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
                         SpectralQty(self.wl, np.array([1.1, 2.4, 3.9, 5.6]) << u.W / (u.m * u.nm)))
        self.assertEqual(SpectralQty(self.wl, np.arange(1, 5, 1) << u.m) * self.sqty,
                         SpectralQty(self.wl, np.array([1.1, 2.4, 3.9, 5.6]) << u.W / (u.m * u.nm)))
        # rebin without extrapolation and without reduction
        self.assertEqual(
            self.sqty * SpectralQty(np.arange(199.5, 204.5, 1) << u.nm, np.arange(1, 6, 1) << u.m),
            SpectralQty(self.wl, [1.65, 3.0, 4.55, 6.3] * u.W / (u.m * u.nm)))
        # rebin without extrapolation and with reduction
        self.assertEqual(
            self.sqty * SpectralQty(np.arange(200.5, 204.5, 1) << u.nm, np.arange(1, 5, 1) << u.m, fill_value=False),
            SpectralQty(np.arange(201, 204) << u.nm, np.array([1.8, 3.25, 4.9]) << u.W / (u.m * u.nm)))
        # lambda
        self.assertEqual(self.sqty * (lambda wl: 0.7 * u.dimensionless_unscaled),
                         SpectralQty(self.wl, self.qty * 0.7))

    def test___truediv__(self):
        # Integer
        self.assertEqual(self.sqty / 2, SpectralQty(np.arange(200, 204, 1) << u.nm,
                                                    np.arange(5.5e-1, 7.5e-1, 5e-2) << u.W / (u.m ** 2 * u.nm)))
        # Float
        self.assertEqual(self.sqty / 2., SpectralQty(np.arange(200, 204, 1) << u.nm,
                                                     np.arange(5.5e-1, 7.5e-1, 5e-2) << u.W / (u.m ** 2 * u.nm)))
        # SpectralQty
        self.assertEqual(self.sqty / SpectralQty(self.wl, np.arange(1, 5, 1) << u.m),
                         SpectralQty(self.wl, np.array([1.1, 0.6, 1.3 / 3, 0.35]) << u.W / (u.m ** 3 * u.nm)))
        # rebin without extrapolation and without reduction
        self.assertEqual(
            self.sqty / SpectralQty(np.arange(199.5, 204.5, 1) << u.nm, np.arange(1, 6, 1) << u.m),
            SpectralQty(self.wl, [1.1 / 1.5, 1.2 / 2.5, 1.3 / 3.5, 1.4 / 4.5] * u.W / (u.m ** 3 * u.nm)))
        # rebin without extrapolation and with reduction
        self.assertEqual(
            self.sqty / SpectralQty(np.arange(200.5, 204.5, 1) << u.nm, np.arange(1, 5, 1) << u.m, fill_value=False),
            SpectralQty(np.arange(201, 204) << u.nm, np.array([1.2 / 1.5, 1.3 / 2.5, 1.4 / 3.5]) << u.W /
                        (u.m ** 3 * u.nm)))
        # lambda
        self.assertEqual(self.sqty / (lambda wl: 0.7 * u.dimensionless_unscaled),
                         SpectralQty(self.wl, self.qty / 0.7))

    def test___pow__(self):
        # Integer
        self.assertEqual(self.sqty ** 2, SpectralQty(self.wl, self.qty ** 2))
        # Float
        self.assertEqual(self.sqty ** 0.5, SpectralQty(self.wl, self.qty ** 0.5))

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
            self.sqty - SpectralQty(np.arange(200.5, 204.5, 1) << u.nm, np.arange(1, 5, 1) << u.W / (u.m ** 2 * u.nm),
                                    fill_value=False),
            SpectralQty(np.arange(201, 204) << u.nm, np.array([-0.3, -1.2, -2.1]) << u.W / (u.m ** 2 * u.nm)))
        # lambda
        self.assertEqual(self.sqty - (lambda wl: 1 * u.W / (u.m ** 2 * u.nm ** 2) * wl),
                         SpectralQty(self.wl, np.array([-198.9, -199.8, -200.7, -201.6]) << u.W / (u.m ** 2 * u.nm)))

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
            self.sqty + SpectralQty(np.arange(200.5, 204.5, 1) << u.nm, np.arange(1, 5, 1) << u.W / (u.m ** 2 * u.nm),
                                    fill_value=False),
            SpectralQty(np.arange(201, 204) << u.nm, np.array([2.7, 3.8, 4.9]) << u.W / (u.m ** 2 * u.nm)))
        # lambda
        self.assertEqual(self.sqty + (lambda wl: 1 * u.W / (u.m ** 2 * u.nm ** 2) * wl),
                         SpectralQty(self.wl, np.array([201.1, 202.2, 203.3, 204.4]) << u.W / (u.m ** 2 * u.nm)))

    def test_rebinning(self):
        # Test interpolation
        wl_new = np.arange(200.5, 210.5, 1) << u.nm
        sqty_res = SpectralQty(wl_new[:3], np.array([1.15, 1.25, 1.35]) << u.W / (u.m ** 2 * u.nm))
        sqty_rebin = SpectralQty(self.wl, self.qty, fill_value=False).rebin(wl_new)
        self.assertEqual(sqty_rebin, sqty_res)

        # Test extrapolation
        wl_new = np.arange(200.5, 210.5, 1) << u.nm
        sqty_res = SpectralQty(wl_new, np.array([1.15, 1.25, 1.35, 1.45, 1.55, 1.65, 1.75, 1.85,
                                                 1.95, 2.05]) << u.W / (u.m ** 2 * u.nm))
        sqty_rebin = SpectralQty(self.wl, self.qty, fill_value=True).rebin(wl_new)
        self.assertEqual(sqty_rebin, sqty_res)

        # Test fill value
        wl_new = np.arange(200.5, 210.5, 1) << u.nm
        sqty_res = SpectralQty(wl_new, np.array([1.15, 1.25, 1.35, 0, 0, 0, 0, 0, 0, 0]) << u.W / (u.m ** 2 * u.nm))
        sqty_rebin = SpectralQty(self.wl, self.qty, fill_value=0).rebin(wl_new)
        self.assertEqual(sqty_rebin, sqty_res)

        # Test binning
        self.setUp()
        wl_new = np.arange(200.5, 210, 2) << u.nm
        sqty_res = SpectralQty(wl_new[:2], np.array([1.15, 1.35]) << u.W / (u.m ** 2 * u.nm))
        sqty_rebin = SpectralQty(self.wl, self.qty, fill_value=False).rebin(wl_new)
        self.assertEqual(sqty_rebin, sqty_res)

    def test_fromFile(self):
        sqty = SpectralQty.fromFile("tests/data/target/target_demo_1.csv", u.nm, u.W / (u.m ** 2 * u.nm))
        res = SpectralQty(np.arange(200, 210, 1) << u.nm,
                          np.arange(1.1, 2.1, 0.1) * 1e-15 << u.W / (u.m ** 2 * u.nm))
        self.assertEqual(sqty, res)

        sqty = SpectralQty.fromFile("tests/data/target/target_demo_2.csv", u.nm, u.W / (u.m ** 2 * u.nm))
        self.assertEqual(sqty, res)

    def test_integrate(self):
        integral = self.sqty.integrate()
        self.assertAlmostEqual(integral.value, 3.75)
        self.assertTrue(integral.unit.is_equivalent(u.W / u.m ** 2))
