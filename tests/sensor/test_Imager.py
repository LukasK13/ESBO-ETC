from unittest import TestCase
import astropy.units as u
import numpy as np
from esbo_etc.classes.Config import Configuration
from esbo_etc.classes.target.FileTarget import FileTarget
from esbo_etc.classes.target.BlackBodyTarget import BlackBodyTarget
from esbo_etc.classes.optical_component.StrayLight import StrayLight
from esbo_etc.classes.sensor.Imager import Imager


class TestImager(TestCase):
    def setUp(self):
        self.config = Configuration("data/esbo-etc_defaults.xml").conf
        self.imager_args = dict(quantum_efficiency=0.9 * u.electron / u.photon,
                                pixel_geometry=np.array([1024, 1024]) << u.pix,
                                pixel_size=6.5 * u.um, read_noise=1.4 * u.electron ** 0.5 / u.pix,
                                dark_current=0.6 * u.electron / u.pix / u.second, well_capacity=30000 * u.electron,
                                f_number=13, common_conf=self.config.common, center_offset=np.array([0, 0]) << u.pix,
                                shape="circle", contained_energy="FWHM", contained_pixels=None)
        self.target = FileTarget("data/target/target_demo_1.csv", np.arange(200, 210) << u.nm)
        self.zodiac = StrayLight(self.target, "data/straylight/zodiacal_emission_1.csv")
        self.imager = Imager(self.zodiac, **self.imager_args)

    def test_getSNR(self):
        snr = self.imager.getSNR(0.1 * u.s)
        self.assertAlmostEqual(snr.value, 5.675140880569046)

    def test_getExpTime(self):
        exp_time = 0.1 * u.s
        snr = self.imager.getSNR(exp_time)
        exp_time_ = self.imager.getExpTime(snr)
        self.assertAlmostEqual(exp_time.value, exp_time_.value)

    def test_getSensitivity(self):
        exp_time = 100 * u.s
        target = BlackBodyTarget(np.arange(200, 210) << u.nm, mag=20 * u.mag)
        zodiac = StrayLight(target, "data/straylight/zodiacal_emission_1.csv")
        imager = Imager(zodiac, **self.imager_args)
        snr = imager.getSNR(exp_time)
        target = BlackBodyTarget(np.arange(200, 210) << u.nm, mag=10 * u.mag)
        zodiac = StrayLight(target, "data/straylight/zodiacal_emission_1.csv")
        imager = Imager(zodiac, **self.imager_args)
        sensitivity = imager.getSensitivity(exp_time, snr, 10 * u.mag)
        self.assertAlmostEqual(sensitivity.value, 20)
