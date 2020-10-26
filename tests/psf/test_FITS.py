from unittest import TestCase
from esbo_etc.classes.psf.FITS import FITS
from esbo_etc.classes.psf.Airy import Airy
from esbo_etc.classes.sensor.PixelMask import PixelMask
import astropy.units as u
import numpy as np


class TestFITS(TestCase):
    def setUp(self):
        self.fits = FITS("tests/data/psf_5um.fits", 5.5, 5 * u.um, 0.5 * u.m, 10, 6.5 * u.um)
        self.airy = Airy(5.5, 5 * u.um, 0.5 * u.m, 10, 6.5 * u.um)

    def test_calcReducedObservationAngle(self):
        # No jitter
        self.assertTrue(np.isclose(self.fits.calcReducedObservationAngle(80).value,
                                   self.airy.calcReducedObservationAngle(80).value, rtol=0.04))

        # Jitter
        self.assertTrue(np.isclose(self.fits.calcReducedObservationAngle(80, 1 * u.arcsec).value,
                        self.airy.calcReducedObservationAngle(80, 1 * u.arcsec).value, rtol=0.02))

    def test_mapToPixelArray(self):
        # No jitter
        reduced_observation_angle = self.fits.calcReducedObservationAngle(80).value
        d_ap = (reduced_observation_angle / (6.5 * u.um / (13.0 * 4 * u.um))).decompose() * u.pix
        mask = PixelMask(np.array([1024, 1024]) << u.pix, 6.5 * u.um, np.array([0.5, 0.5]) << u.pix)
        mask.createPhotometricAperture("circle", d_ap / 2)
        mask = self.fits.mapToPixelMask(mask)

        reduced_observation_angle_2 = self.airy.calcReducedObservationAngle(80).value
        d_ap_2 = (reduced_observation_angle_2 / (6.5 * u.um / (13.0 * 4 * u.um))).decompose() * u.pix
        mask_2 = PixelMask(np.array([1024, 1024]) << u.pix, 6.5 * u.um, np.array([0.5, 0.5]) << u.pix)
        mask_2.createPhotometricAperture("circle", d_ap_2 / 2)
        mask_2 = self.airy.mapToPixelMask(mask_2)
        self.assertTrue(np.isclose(float(mask.sum()), float(mask_2.sum()), rtol=0.01))

        # Jitter
        reduced_observation_angle = self.fits.calcReducedObservationAngle(80, 1 * u.arcsec).value
        d_ap = (reduced_observation_angle / (6.5 * u.um / (13.0 * 4 * u.um))).decompose() * u.pix
        mask = PixelMask(np.array([1024, 1024]) << u.pix, 6.5 * u.um, np.array([0.5, 0.5]) << u.pix)
        mask.createPhotometricAperture("circle", d_ap / 2)
        mask = self.fits.mapToPixelMask(mask, 1 * u.arcsec)

        reduced_observation_angle_2 = self.airy.calcReducedObservationAngle(80, 1 * u.arcsec).value
        d_ap_2 = (reduced_observation_angle_2 / (6.5 * u.um / (13.0 * 4 * u.um))).decompose() * u.pix
        mask_2 = PixelMask(np.array([1024, 1024]) << u.pix, 6.5 * u.um, np.array([0.5, 0.5]) << u.pix)
        mask_2.createPhotometricAperture("circle", d_ap_2 / 2)
        mask_2 = self.airy.mapToPixelMask(mask_2, 1 * u.arcsec)
        self.assertTrue(np.isclose(float(mask.sum()), float(mask_2.sum()), rtol=0.03))
