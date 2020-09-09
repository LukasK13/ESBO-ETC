from unittest import TestCase
from esbo_etc import esbo_etc
import logging


class Testesbo_etc(TestCase):
    def test_run(self):
        etc = esbo_etc("tests/data/esbo-etc_defaults.xml", logging.WARNING)
        res = etc.run()
        self.assertAlmostEqual(res.value, 47.29125798685691)
