from unittest import TestCase
from esbo_etc.classes.Config import Configuration
from esbo_etc.classes.RadiantFactory import RadiantFactory
import esbo_etc.classes.optical_component as oc
from esbo_etc.classes.target import BlackBodyTarget
import astropy.units as u


class TestRadiantFactory(TestCase):
    def test_fromConfigBatch(self):
        conf = Configuration("data/esbo-etc_defaults.xml").conf
        factory = RadiantFactory(conf.common.wl_bins())
        parent = factory.fromConfigBatch(conf)

        parent_2 = BlackBodyTarget(conf.common.wl_bins(), 5778 * u.K, 10 * u.mag, "V")
        parent_2 = oc.Atmosphere(parent_2, "data/atmosphere/transmittance.csv", "data/atmosphere/emission.csv")
        parent_2 = oc.StrayLight(parent_2, "data/straylight/emission.csv")
        parent_2 = oc.Mirror(parent_2, "data/mirror/reflectance.csv", "data/mirror/emissivity.csv", 70 * u.K,
                             obstruction=0.1, obstructor_temp=70 * u.K)
        parent_2 = oc.Mirror(parent_2, "data/mirror/reflectance.csv", "data/mirror/emissivity.csv", 70 * u.K)
        parent_2 = oc.Mirror(parent_2, "data/mirror/reflectance.csv", "data/mirror/emissivity.csv", 70 * u.K)
        parent_2 = oc.Filter.fromRange(parent_2, 400 * u.nm, 480 * u.nm, "data/filter/emissivity.csv", 70 * u.K)
        parent_2 = oc.Lens(parent_2, "data/lens/transmittance.csv", "data/lens/emissivity.csv", 70 * u.K)

        self.assertEqual(parent.calcSignal()[0], parent_2.calcSignal()[0])
        self.assertEqual(parent.calcBackground(), parent_2.calcBackground())
