from unittest import TestCase
from esbo_etc.classes.optical_component.Mirror import Mirror
from esbo_etc.classes.SpectralQty import SpectralQty
from esbo_etc.classes.target.FileTarget import FileTarget
import astropy.units as u
import numpy as np


class TestMirror(TestCase):
    wl = np.arange(201, 205, 1) << u.nm

    def setUp(self):
        self.target = FileTarget("data/target/target_demo_1.csv", self.wl)
        self.mirror = Mirror(self.target, "data/mirror/mirror_reflectance.csv", 0.5, temp=300 * u.K)

    def test___init__(self):
        self.assertEqual(self.mirror.calcNoise(),
                         SpectralQty(self.wl, [4.31413931e-96, 1.37122214e-95, 4.30844544e-95, 1.33846280e-94] << u.W /
                                     (u.m ** 2 * u.nm * u.sr)))
        self.assertEqual(self.mirror.calcSignal(),
                         SpectralQty(self.wl, [1.20e-15, 1.30e-15, 1.40e-15, 1.35e-15] << u.W / (u.m ** 2 * u.nm)))
