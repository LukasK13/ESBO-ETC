from unittest import TestCase
import astropy.units as u
import numpy as np
from esbo_etc.classes.Config import Configuration
from esbo_etc.classes.target.FileTarget import FileTarget
from esbo_etc.classes.target.BlackBodyTarget import BlackBodyTarget
from esbo_etc.classes.optical_component.Atmosphere import Atmosphere
from esbo_etc.classes.optical_component.CosmicBackground import CosmicBackground
from esbo_etc.classes.optical_component.Mirror import Mirror
from esbo_etc.classes.sensor.Heterodyne import Heterodyne


class TestHeterodyne(TestCase):
    def setUp(self):
        self.config = Configuration("tests/data/esbo-etc_defaults_heterodyne.xml").conf
        self.heterodyne_args = dict(aperture_efficiency=0.55, main_beam_efficiency=0.67,
                                    receiver_temp=1050 * u.K, eta_fss=0.97, lambda_line=157.774 * u.um, kappa=1.0,
                                    common_conf=self.config.common)
        self.target = FileTarget("tests/data/target/line.csv", self.config.common.wl_bins())
        self.atmosphere = Atmosphere(self.target, "tests/data/atmosphere/transmittance_great.csv")
        self.cosmic = CosmicBackground(self.atmosphere, temp=220 * u.K, emissivity=0.14)
        self.mirror = Mirror(self.cosmic, reflectance="tests/data/mirror/reflectance_great.csv", emissivity=0.08,
                             temp=230 * u.K)
        self.heterodyne = Heterodyne(self.mirror, **self.heterodyne_args)

    def test_getSNR(self):
        snr = self.heterodyne.getSNR(1900 * u.s)
        self.assertAlmostEqual(snr.value, 10.059625717085497)

    def test_getExpTime(self):
        exp_time = 1900 * u.s
        snr = self.heterodyne.getSNR(exp_time)
        exp_time_ = self.heterodyne.getExpTime(snr)
        self.assertAlmostEqual(exp_time.value, exp_time_.value)

    def test_getSensitivity(self):
        exp_time = 1900 * u.s
        target = BlackBodyTarget(self.config.common.wl_bins(), mag=20 * u.mag)
        atmosphere = Atmosphere(target, "tests/data/atmosphere/transmittance_great.csv")
        cosmic = CosmicBackground(atmosphere, temp=220 * u.K, emissivity=0.14)
        mirror = Mirror(cosmic, reflectance="tests/data/mirror/reflectance_great.csv", emissivity=0.08, temp=230 * u.K)
        heterodyne = Heterodyne(mirror, **self.heterodyne_args)
        snr = heterodyne.getSNR(exp_time)
        target = BlackBodyTarget(self.config.common.wl_bins(), mag=10 * u.mag)
        atmosphere = Atmosphere(target, "tests/data/atmosphere/transmittance_great.csv")
        cosmic = CosmicBackground(atmosphere, temp=220 * u.K, emissivity=0.14)
        mirror = Mirror(cosmic, reflectance="tests/data/mirror/reflectance_great.csv", emissivity=0.08, temp=230 * u.K)
        heterodyne = Heterodyne(mirror, **self.heterodyne_args)
        sensitivity = heterodyne.getSensitivity(exp_time, snr, 10 * u.mag)
        self.assertAlmostEqual(sensitivity.value, 20)
