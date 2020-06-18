from unittest import TestCase
from esbo_etc.classes.psf.Zemax import Zemax
from esbo_etc.classes.sensor.PixelMask import PixelMask
import astropy.units as u
import numpy as np


class TestZemax(TestCase):
    def setUp(self):
        self.zemax = Zemax("data/psf_2um.txt", 13, 4 * u.um, 0.5 * u.m, 13, 6.5 * u.um)

    def test_calcReducedObservationAngle(self):
        # No jitter
        self.assertAlmostEqual(self.zemax.calcReducedObservationAngle(80).value, 1.6563253147273092)

        # Jitter
        self.assertAlmostEqual(self.zemax.calcReducedObservationAngle(80, 1 * u.arcsec).value, 2.5910983637231553)

    def test_mapToPixelArray(self):
        # No jitter
        reduced_observation_angle = self.zemax.calcReducedObservationAngle(80).value
        d_ap = (reduced_observation_angle / (6.5 * u.um / (13.0 * 4 * u.um))).decompose() * u.pix
        mask = PixelMask(np.array([1024, 1024]) << u.pix, 6.5 * u.um, np.array([0.5, 0.5]) << u.pix)
        mask.createPhotometricAperture("circle", d_ap / 2)
        mask = self.zemax.mapToPixelMask(mask)
        self.assertAlmostEqual(float(mask.sum()), 0.8503792384734423)

        # Jitter
        reduced_observation_angle = self.zemax.calcReducedObservationAngle(80, 1 * u.arcsec).value
        d_ap = (reduced_observation_angle / (6.5 * u.um / (13.0 * 4 * u.um))).decompose() * u.pix
        mask = PixelMask(np.array([1024, 1024]) << u.pix, 6.5 * u.um, np.array([0.5, 0.5]) << u.pix)
        mask.createPhotometricAperture("circle", d_ap / 2)
        mask = self.zemax.mapToPixelMask(mask, 1 * u.arcsec)
        self.assertAlmostEqual(float(mask.sum()), 0.8260381847048797)
