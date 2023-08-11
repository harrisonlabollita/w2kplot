import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.lines import Line2D
import types
from typing import Union, List, Dict

from . import w2kplot_base_style, w2kplot_bands_style


# WannierBands class object
class WannierBands(object):
    # TODO: would it be possible to get high-symmetry points
    # for just a Wannier band plot?

    def __init__(self, wann_bands: str = None, case: str = None) -> None:
        """
        Initialze the WannierBands object.

        Parameters
        ----------
        wann_bands  : string, optional
                      Filename of Wannier90 *_band.dat file.
        """
        self.bohr_to_ang = 0.53
        if case and not wann_bands:
            self.wann_bands = case + '_band.dat'
        else:
            self.wann_bands = wann_bands

        if self.wann_bands is None:
            try:
                self.wann_bands = glob.glob("*_band.dat")[0]
            except BaseException:
                raise FileNotFoundError(
                    "Could not find a case_band.dat file in this directory\n. Please provide a case_band.dat file!")
        self.kpts, self.wann_bands = self._get_wannier_bands()

    def _get_wannier_bands(self):
        """
        internal function for parsing the Wannier90 band.dat file.
        """
        data = np.loadtxt(self.wann_bands)
        kpts = np.unique(data[:, 0]) * self.bohr_to_ang
        wann_bands = data[:, 1].reshape(int(len(data) / len(kpts)), len(kpts))
        return kpts, wann_bands

# Wannier90 bands plotting


def wannier_band_plot(wannier_bands,
                      *opt_list,
                      **opt_dict): __wannier_band_plot(plt,
                                                       wannier_bands,
                                                       *opt_list,
                                                       **opt_dict)


def __wannier_band_plot(figure, wannier_bands, *opt_list, **opt_dict):
    if isinstance(figure, types.ModuleType):
        figure = figure.gca()

    try:
        # new version of matplotlib
        grid_spec = figure.get_subplotspec()
        is_first_col = grid_spec.is_first_col()
    except BaseException:
        # old version of matplotlib
        is_first_col = figure.is_first_col()

    # plot the wannier bands
    for b in range(len(wannier_bands.wann_bands)):
        figure.plot(wannier_bands.kpts,
                    wannier_bands.wann_bands[b, :], *opt_list, **opt_dict)

    # decorate the figure from here
    figure.axhline(0.0, color="k", lw=1, ls='dotted')
    if is_first_col:
        figure.set_ylabel(r"$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)")

    figure.set_ylim(-2, 2)
    figure.set_xlim(wannier_bands.kpts[0], wannier_bands.kpts[-1])


plt.style.use([w2kplot_base_style, w2kplot_base_style])
mpl.axes.Axes.wannier_band_plot = lambda self, wannier_bands, * \
    opt_list, **opt_dict: __wannier_band_plot(self, wannier_bands, *opt_list, **opt_dict)
