from unittest import TestCase
from esbo_etc.classes.optical_component.AHotOpticalComponent import AHotOpticalComponent
from esbo_etc.classes.IRadiant import IRadiant
from esbo_etc.classes.SpectralQty import SpectralQty
from esbo_etc.classes.target.FileTarget import FileTarget
import astropy.units as u
import numpy as np
from typing import Union


class HotOpticalComponent(AHotOpticalComponent):
    def __init__(self, parent: IRadiant, emissivity: Union[SpectralQty, int, float, str], temp: u.Quantity,
                 obstruction: float = 0, obstructor_temp: u.Quantity = 0 * u.K, obstructor_emissivity: float = 1):
        super().__init__(parent, emissivity, temp, obstruction, obstructor_temp, obstructor_emissivity)

    def _propagate(self, sqty: SpectralQty) -> SpectralQty:
        return sqty


class TestAHotOpticalComponent(TestCase):
    wl = np.arange(201, 205, 1) << u.nm

    def setUp(self):
        self.target = FileTarget("data/target/target_demo_1.csv", self.wl)

    def test___init__(self):
        comp = HotOpticalComponent(self.target, SpectralQty(self.wl, np.repeat(0.5, 4) << u.dimensionless_unscaled),
                                   temp=300 * u.K)
        self.assertEqual(comp.calcNoise(),
                         SpectralQty(self.wl, np.array([4.31413931e-96, 1.37122214e-95, 4.30844544e-95,
                                                        1.33846280e-94]) << u.W / (u.m ** 2 * u.nm * u.sr)))

        comp = HotOpticalComponent(self.target, "data/mirror/mirror_emissivity.csv", temp=300 * u.K)
        self.assertEqual(comp.calcNoise(),
                         SpectralQty(self.wl, np.array([4.31413931e-96, 1.37122214e-95, 4.30844544e-95,
                                                        1.33846280e-94]) << u.W / (u.m ** 2 * u.nm * u.sr)))
