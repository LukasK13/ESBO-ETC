from unittest import TestCase
from esbo_etc.classes.psf.Zemax import Zemax
import astropy.units as u


class TestZemax(TestCase):
    def setUp(self):
        self.zemax = Zemax("data/psf.txt", 13, 4 * u.um, 0.5 * u.m)

    def test_calcReducedObservationAngle(self):
        self.assertAlmostEqual(self.zemax.calcReducedObservationAngle(0.6595336151196701).value, 0.08284705528846155)
