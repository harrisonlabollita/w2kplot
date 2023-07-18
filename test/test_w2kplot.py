import glob, os, time
import numpy as np
import matplotlib.pyplot as plt

from w2kplot.bands import Bands, FatBands, band_plot, fatband_plot
from w2kplot.utils import make_label
from w2kplot.structure import Structure

import unittest

spaghetti = glob.glob(os.getcwd() + "/test/*spaghetti_ene")[0]
klist_band = glob.glob(os.getcwd() + "/test/*klist_band")[0]
target_Ek = np.loadtxt(glob.glob(os.getcwd() + "/test/*dat")[0])
struct_file = glob.glob(os.getcwd() + "/test/*struct")[0]


class Testw2kplot(unittest.TestCase):

    def test_structure(self):
        struct    = Structure(struct_file)
        self.assertEqual(len(struct), 4)

        ref_atoms = { 0 :  ['Cs1', 1 ],
                  1 :  ['V',   3 ],
                  2 :  ['Sb1', 1 ],
                  3 :  ['Sb2', 4 ]
                  }
        for key in ref_atoms.keys():
            aspec, amult = ref_atoms[key]
            tspec, tmult = struct[key]
            print(f'ref: {aspec}, {amult}, parsed: {tspec}, {tmult}')
            self.assertEqual(aspec, tspec)
            self.assertEqual(amult, tmult)

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
            fig, ax = plt.subplots(1, 2, sharey=True, figsize=(6, 3))
            up_channel = Bands(spaghetti="examples/la112sp/la112sp.spaghettiup_ene",
                               klist_band="examples/la112sp/la112sp.klist_band")
            dn_channel = Bands(spaghetti="examples/la112sp/la112sp.spaghettidn_ene",
                               klist_band="examples/la112sp/la112sp.klist_band")
            ax[0].band_plot(up_channel, "b-", lw=1)
            ax[0].set_title('majority')
            ax[1].band_plot(dn_channel, "r-", lw=1)
            ax[1].set_title('minority')
            plt.subplots_adjust(hspace=0.05)
            return (time.time() - start)

        def csv3sb5():
            start = time.time()
            dft = FatBands(
                # 2 = V, 3=Sb1, 4=Sb2 (see struct file)
                atoms=[2, 4, 3],
                # 7=d, 3=p, 3=p (see header of qtl file)
                orbitals=[[7], [3], [3]],
                colors=[['dodgerblue'], ['forestgreen'], ['tomato']],
                weight=50,
                spaghetti='examples/csv3sb5/cs35.spaghetti_ene',  # get ek
                klist_band='examples/csv3sb5/cs35.klist_band',   # get kpts
                eF='examples/csv3sb5/cs35.scf',                  # get eF
                qtl='examples/csv3sb5/cs35.qtl',                 # get ⟨Ψ|ϕ⟩
                struct='examples/csv3sb5/cs35.struct',           # get structure information
            )

            fig, ax = plt.subplots(figsize=(3, 3))
            ax.fatband_plot(dft, "k-", lw=1.5)
            fig.legend(handles=dft.create_legend(), ncol=3, loc="upper center")
            return (time.time() - start)

        funcs = [la112sp, csv3sb5]
        runtimes = [1, 6]
        for fun, rt in zip(funcs, runtimes):
            run = fun()
            print("executed example ", fun.__name__, " in ", run, "s")
            self.assertLessEqual(run, rt)


if __name__ == "__main__":
    unittest.main()
