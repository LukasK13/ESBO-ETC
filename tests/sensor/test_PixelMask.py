from unittest import TestCase
from esbo_etc.classes.sensor.PixelMask import PixelMask
import numpy as np
import astropy.units as u


class TestPixelMask(TestCase):
    def setUp(self):
        self.mask = PixelMask(np.array([10, 8]) << u.pix, 6.5 * u.um, center_offset=np.array([0.2, 0.5]) << u.pix)

    def test___new__(self):
        self.assertTrue((self.mask.view(np.ndarray) == np.zeros((8, 10))).all())
        self.assertEqual(self.mask.center_ind, [3.5, 4.5])
        self.assertEqual(self.mask.psf_center_ind, [4.0, 4.7])
        self.assertEqual(self.mask.pixel_geometry, [8 * u.pix, 10 * u.pix])

    def test_createPhotometricAperture(self):
        # circle
        self.mask.createPhotometricAperture("circle", 2.3 * u.pix)
        res = np.array([[0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                        [0., 0., 0., 1., 1., 1., 1., 0., 0., 0.],
                        [0., 0., 0., 1., 1., 1., 1., 1., 0., 0.],
                        [0., 0., 1., 1., 1., 1., 1., 1., 0., 0.],
                        [0., 0., 0., 1., 1., 1., 1., 1., 0., 0.],
                        [0., 0., 0., 1., 1., 1., 1., 0., 0., 0.],
                        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]])
        self.assertTrue((self.mask.view(np.ndarray) == res).all())

        self.setUp()
        self.mask.createPhotometricAperture("circle", 2.6 * u.pix, np.array([-0.5, 0.8]) << u.pix)
        res = np.array([[0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                        [0., 0., 0., 1., 1., 1., 0., 0., 0., 0.],
                        [0., 0., 1., 1., 1., 1., 1., 0., 0., 0.],
                        [0., 1., 1., 1., 1., 1., 1., 1., 0., 0.],
                        [0., 1., 1., 1., 1., 1., 1., 1., 0., 0.],
                        [0., 0., 1., 1., 1., 1., 1., 0., 0., 0.],
                        [0., 0., 0., 1., 1., 1., 0., 0., 0., 0.]])
        self.assertTrue((self.mask.view(np.ndarray) == res).all())

        # square
        self.setUp()
        self.mask.createPhotometricAperture("square", 2.3 * u.pix)
        res = np.array([[0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                        [0., 0., 1., 1., 1., 1., 1., 1., 0., 0.],
                        [0., 0., 1., 1., 1., 1., 1., 1., 0., 0.],
                        [0., 0., 1., 1., 1., 1., 1., 1., 0., 0.],
                        [0., 0., 1., 1., 1., 1., 1., 1., 0., 0.],
                        [0., 0., 1., 1., 1., 1., 1., 1., 0., 0.],
                        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]])
        self.assertTrue((self.mask.view(np.ndarray) == res).all())
