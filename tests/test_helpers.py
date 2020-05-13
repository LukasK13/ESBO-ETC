from unittest import TestCase
from esbo_etc.lib.helpers import rasterizeCircle
import numpy as np


class Test(TestCase):
    def test_rasterize_circle(self):
        grid = np.zeros((8, 8))
        circ = rasterizeCircle(grid, 2.6, 4.5, 3.8)
        circ_ex = np.array([[0., 0., 0., 0., 0., 0., 0., 0.],
                            [0., 0., 0., 0., 1., 1., 0., 0.],
                            [0., 0., 0., 1., 1., 1., 1., 0.],
                            [0., 0., 1., 1., 1., 1., 1., 1.],
                            [0., 0., 1., 1., 1., 1., 1., 1.],
                            [0., 0., 1., 1., 1., 1., 1., 1.],
                            [0., 0., 0., 1., 1., 1., 1., 0.],
                            [0., 0., 0., 0., 0., 0., 0., 0.]])
        self.assertTrue((circ == circ_ex).all())
