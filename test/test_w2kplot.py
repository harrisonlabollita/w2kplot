import unittest
import glob, os
from w2kplot import Bands
import numpy as np

spaghetti = glob.glob(os.getcwd() + "/test/*spaghetti_ene")[0]
klist_band = glob.glob(os.getcwd() + "/test/*klist_band")[0]
target_Ek = np.loadtxt(glob.glob(os.getcwd() + "/test/*dat")[0])


class Testw2kplot(unittest.TestCase):

    def test_klist_band_parser(self):
        dft = Bands(spaghetti=spaghetti, klist_band=klist_band)
        target_hsl = ['$\\Gamma$', 'X', 'M', '$\\Gamma$', 'Z', 'R', 'A', 'Z']
        target_hsp = np.array([0.0, 0.2976, 0.59521, 1.01609, 1.5094, 1.807, 2.10461, 2.52548])
        self.assertEqual(dft.high_symmetry_labels, target_hsl)
        np.testing.assert_allclose(dft.high_symmetry_points, target_hsp)

    def test_spaghetti_parser(self):
        dft = Bands(spaghetti=spaghetti, klist_band=klist_band)
        np.testing.assert_allclose(dft.Ek, target_Ek)

if __name__ == "__main__":
    unittest.main()
