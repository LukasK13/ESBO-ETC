from unittest import TestCase
from esbo_etc.classes import *
import astropy.units as u
import numpy as np


class OpticalComponent(AOpticalComponent):
    def __init__(self, parent: IRadiant, transreflectivity: SpectralQty = None,
                 noise: SpectralQty = None, obstruction: float = 0, obstructor_temp: u.Quantity = 0 * u.K,
                 obstructor_emissivity: float = 0):
        super().__init__(parent, transreflectivity, noise, obstruction, obstructor_temp, obstructor_emissivity)

    @staticmethod
    def check_config(conf: Entry) -> Union[None, str]:
        pass


class TestAOpticalComponent(TestCase):
    wl = np.arange(4, 8, 1) << u.um

    def setUp(self):
        self.target = BlackBodyTarget(self.wl, temp=5778 * u.K, mag=10 * u.mag, band="U")
        self.comp = OpticalComponent(self.target, SpectralQty(self.wl, np.repeat(0.5, 4) << u.dimensionless_unscaled),
                                     SpectralQty(self.wl, np.repeat(1e-5, 4) << u.W / (u.m ** 2 * u.nm * u.sr)),
                                     obstruction=0.1, obstructor_temp=300 * u.K, obstructor_emissivity=1)

    def test_calcSignal(self):
        self.assertEqual(self.comp.calcSignal()[0],
                         SpectralQty(self.wl, np.array([1.29074440e-17, 5.65909989e-18, 2.85372997e-18,
                                                        1.58973516e-18]) << u.W / (u.m ** 2 * u.nm)))

    def test_calcBackground(self):
        self.assertEqual(self.comp.calcBackground(),
                         SpectralQty(self.wl, np.array([8.21976423e-05, 2.70268340e-04, 5.27503292e-04,
                                                        7.60597616e-04]) << u.W / (u.m ** 2 * u.nm * u.sr)))
        comp = OpticalComponent(self.comp, SpectralQty(self.wl, np.repeat(0.5, 4) << u.dimensionless_unscaled),
                                SpectralQty(self.wl, np.repeat(0, 4) << u.W / (u.m ** 2 * u.nm * u.sr)),
                                obstruction=0.1, obstructor_temp=300 * u.K, obstructor_emissivity=1)
        self.assertEqual(comp.calcBackground(),
                         SpectralQty(self.wl, np.array([1.09186581e-04, 3.81889092e-04, 7.54879773e-04,
                                                        10.92866544e-04]) << u.W / (u.m ** 2 * u.nm * u.sr)))
