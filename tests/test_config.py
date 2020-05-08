from unittest import TestCase
from esbo_etc.classes.Config import Configuration, Entry
import astropy.units as u


class TestConfiguration(TestCase):
    def setUp(self):
        self.config = Configuration("data/esbo-etc_defaults.xml")

    def test_signal(self):
        self.assertTrue(isinstance(self.config.conf, Entry))
        self.assertTrue(
            {"common", "astroscene", "common_optics", "instrument"}.issubset(self.config.conf.__dir__()))
        self.assertTrue({"wl_min", "wl_max", "wl_delta", "d_aperture", "jitter_sigma", "output_path",
                         "wl_bins"}.issubset(self.config.conf.common.__dir__()))
        self.assertTrue(self.config.conf.common.wl_min().unit.is_equivalent(u.meter))
