from unittest import TestCase
from esbo_etc.classes.psf.Airy import Airy
import astropy.units as u


class TestAiry(TestCase):
    def setUp(self):
        self.airy = Airy(13, 4 * u.um, 0.5 * u.m, 10, 6.5 * u.um)

    def test_calc_reduced_observation_angle(self):
        # No jitter, unobstructed
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("peak").value, 0.0)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("fwhm").value, 1.028)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("min").value, 2.44)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle(80.).value, 1.7938842051009245)

        # Jitter, unobstructed
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("peak", 1 * u.arcsec).value, 0.0)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("fwhm", 1 * u.arcsec).value, 1.75)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("min", 1 * u.arcsec).value, 3.375)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle(80., 1 * u.arcsec).value, 3.1)

        # No jitter, obstructed
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("peak", obstruction=0.04).value, 0.0)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("fwhm", obstruction=0.04).value, 1.006752080603888)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("min", obstruction=0.04).value, 2.33301171875)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle(80., obstruction=0.04).value, 3.1045076425044726)

        # Jitter, obstructed
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("peak", 1 * u.arcsec, 0.04).value, 0.0)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("fwhm", 1 * u.arcsec, 0.04).value, 1.725)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("min", 1 * u.arcsec, 0.04).value, 2.875)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle(80., 1 * u.arcsec, 0.04).value, 3.1)
