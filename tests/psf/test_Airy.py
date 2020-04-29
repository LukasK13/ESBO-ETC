from unittest import TestCase
from esbo_etc.classes.psf.Airy import Airy
import astropy.units as u


class TestAiry(TestCase):
    def setUp(self):
        self.airy = Airy(4 * u.um, 0.5 * u.m)

    def test_calc_reduced_observation_angle(self):
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("peak").value, 0.0)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("fwhm").value, 1.028)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("min").value, 2.44)
        self.assertAlmostEqual(self.airy.calcReducedObservationAngle("80").value, 1.7938842051009245)
