from unittest import TestCase
from esbo_etc.classes.psf.Zemax import Zemax
import astropy.units as u


class TestZemax(TestCase):
    def setUp(self):
        self.zemax = Zemax("data/psf_2um.txt", 13, 4 * u.um, 0.5 * u.m, 13, 6.5 * u.um)

    def test_calcReducedObservationAngle(self):
        # No jitter
        self.assertAlmostEqual(self.zemax.calcReducedObservationAngle(80).value, 0.849307235849535)

        # Jitter
        self.assertAlmostEqual(self.zemax.calcReducedObservationAngle(80, 1 * u.arcsec).value, 1.3057369866992834)
