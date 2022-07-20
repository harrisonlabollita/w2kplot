import glob, os
import time
from w2kplot import Bands, FatBands
import numpy as np
import matplotlib.pyplot as plt

import unittest

spaghetti = glob.glob(os.getcwd() + "/test/*spaghetti_ene")[0]
klist_band = glob.glob(os.getcwd() + "/test/*klist_band")[0]
target_Ek = np.loadtxt(glob.glob(os.getcwd() + "/test/*dat")[0])


class Testw2kplot(unittest.TestCase):

    def test_style_sheet(self):
        def try_import():
            worked = False
            try:
                plt.style.use("w2kplot")
                worked = True
            except:
                worked = False
            return worked
        self.assertEqual(try_import(), True)

    def test_klist_band_parser(self):
        dft = Bands(spaghetti=spaghetti, klist_band=klist_band)
        target_hsl = ['$\\Gamma$', 'X', 'M', '$\\Gamma$', 'Z', 'R', 'A', 'Z']
        target_hsp = np.array([0.0, 0.2976, 0.59521, 1.01609, 1.5094, 1.807, 2.10461, 2.52548])
        self.assertEqual(dft.high_symmetry_labels, target_hsl)
        np.testing.assert_allclose(dft.high_symmetry_points, target_hsp)

    def test_spaghetti_parser(self):
        dft = Bands(spaghetti=spaghetti, klist_band=klist_band)
        np.testing.assert_allclose(dft.Ek, target_Ek)


    def test_examples(self):

        def la112sp():
            start = time.time()
            fig, ax = plt.subplots(1,2,sharey=True, figsize=(6,3))
            up_channel=Bands(spaghetti="examples/la112sp/la112sp.spaghettiup_ene",
                             klist_band="examples/la112sp/la112sp.klist_band")
            dn_channel=Bands(spaghetti="examples/la112sp/la112sp.spaghettidn_ene",
                             klist_band="examples/la112sp/la112sp.klist_band")
            ax[0].band_plot(up_channel, "b-", lw=1); ax[0].set_title('majority')
            ax[1].band_plot(dn_channel, "r-", lw=1); ax[1].set_title('minority')
            ax[1].set_ylabel("") # remove the y-label from this subplot
            plt.subplots_adjust(hspace=0.05)
            return (time.time()-start)

        def csv3sb5():
            start = time.time()
            dft = FatBands(
                           atoms=[2,4,3],                 # 2 = V, 3=Sb1, 4=Sb2 (see struct file)
                           orbitals=[[7],[3],[3]], # 7=d, 3=p, 3=p (see header of qtl file)
                           colors=[['dodgerblue'],['forestgreen'],['tomato']],
                           weight  = 50,
                           spaghetti='examples/csv3sb5/cs35.spaghetti_ene', # get ek
                           klist_band='examples/csv3sb5/cs35.klist_band',   # get kpts
                           eF='examples/csv3sb5/cs35.scf',                  # get eF
                           qtl='examples/csv3sb5/cs35.qtl',                 # get ⟨Ψ|ϕ⟩
                           struct='examples/csv3sb5/cs35.struct',           # get structure information
                           )

            fig, ax = plt.subplots(figsize=(3,3))
            ax.fatband_plot(dft, "k-", lw=1.5)
            fig.legend(handles=dft.create_legend(), ncol=3, loc="upper center")
            return (time.time()-start)


        funcs = [la112sp, csv3sb5]
        for fun in funcs:
            print("executed example ", fun.__name__, " in ", fun(), "s")




if __name__ == "__main__":
    unittest.main()
