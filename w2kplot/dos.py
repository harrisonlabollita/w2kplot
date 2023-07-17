# -*- coding: utf-8 -*-

##########################################################################
#
# w2kplot: a thin Python wrapper around matplotlib
#
# Copyright (C) 2022 Harrison LaBollita
# Authors: H. LaBollita
#
# w2kplot is free software licensed under the terms of the MIT license.
#
##########################################################################

import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.lines import Line2D
import types
from typing import Union, List, Dict

try: plt.style.use("w2kplot")
except BaseException: raise ImportError("Could not find install w2kplot style sheet!")


class DensityOfStates(object):
    def __init__(self, dos: List[str] = None,
                 dos_dict: Dict[int, str] = None,
                 sumdos: Union[List[List[int]], bool] = None,
                 colors: List[str] = None,
                 orientation: str = "horizontal"
                 ) -> None:
        """
        Initialize the DensityOfStates object.

        Parameters
        ----------
        dos         : list[string], optional
                     A list of dosfiles to be parsed and plotted.
        dos_dict    : dict[int, str], optional
                     A dictionary mapping the column names in the dosfiles to
                     desired name in plot legend.
        sumdos      : union[list[list[int]], bool], optional
                     A nested of list of how to sum density of states from different columns
        colors      : ist[str], optional
                     A list of matplotlib colors for each dos. Must match the number of keys
                     in the dos_dict
        orientation : string, optional
                     Plot the dos horizontally (horizontal) or vertically (vertical)
        """
        # TODO: need to work on the sumdos featture. For now the user will
        # provide how to sum by hand.
        self.dos = dos
        self.dos_dict = dos_dict
        self.sumdos = sumdos
        self.colors = colors
        self.orientation = orientation

        if self.colors is not None:
            assert len(self.colors) == len(self.dos_dict.keys()
                                           ), "incorrect number of colors for dos!"

        if self.dos_dict is None and self.sumdos is not None:
            raise NotImplementedError(
                "Unfortanately, this is feature is not valid. Please provide a valid dictionary of labels")

        if self.dos is None:
            try:
                self.dos = glob.glob("*.dos*")
            except BaseException:
                raise FileNotFoundError(
                    "Could not find any files matching case.dosXev, where X is a number")

        if self.dos_dict is None:
            # if a dictionary mapping each column to a name is not provided we
            # will build one
            self.dos_dict = {}
            offset = 0
            for file in self.dos:
                headers = open(file).readlines()[2].split()[
                    2:]  # skips the # and ENERGY
                for h in range(len(headers)):
                    self.dos_dict[h + offset] = headers[h]
                offset += len(headers)
        self.energy, self.density_of_states = self.get_dos()

    def get_dos(self):
        """
        internal function to parse the density of state files
        """
        density_of_states = []
        data = np.loadtxt(self.dos[0], comments='#')
        for file in self.dos[1:]: 
            tmp = np.loadtxt(file, comments='#')[:,1:]
            data = np.hstack((data, tmp))

        energy = data[:, 0]
        dos_data = data[:, 1:]
        print(dos_data.shape)
        if self.sumdos is not None:
            place = 0
            dos = np.zeros((len(energy), len(self.sumdos)))
            for to_sum in self.sumdos:
                dos[:, place] = np.mean(dos_data[:, to_sum], axis=1)
                place += 1

            #tosum = self.sumdos
            #one_dim = True
            #try:
            #    check = [item for sublist in tosum for item in sublist]
            #    one_dim = False
            #except TypeError:
            #    check = [item for item in tosum]

            #dos = np.zeros((len(energy), len(tosum)))
            #place = 0
            #for col in range(dos_data.shape[1]):
            #    if col not in check:
            #        dos[:, place] = dos_data[:, col]
            #        place += 1
            #if one_dim:
            #    dos[:, place] = np.mean(dos_data[:, tosum], axis=1)
            #else:
            #    for add in tosum:
            #        dos[:, place] = np.mean(dos_data[:, add], axis=1)
            #        place += 1
            #if "dn" in file:
            #    density_of_states.append(-1 * dos)
            #else:
            density_of_states.append(dos)
        else:
            #if "dn" in file:
            #    density_of_states.append(-1 * dos_data)
            #else:
            density_of_states.append(dos_data)
        return energy, density_of_states

    def smooth_dos(self, fwhm: float) -> None:
        """
        A Gaussian smoothing function to smear out the harsh peaks in the density of states
        when a small broadening was used.

        Parameters
        ----------

        fwhm    : float, required
                  Full width Half Maximum for gaussian smearing converts to σ.
        """

        def fwhm2sigma(fwhm):
            return fwhm / np.sqrt(8 * np.log(2))

        def blur(ie, e):
            kernel = np.exp(-(energy - e)**2 / (2 * sigma**2))
            kernel /= np.sum(kernel)  # normalize
            return np.sum(rho * kernel)

        sigma = fwhm2sigma(fwhm)
        smoother = np.vectorize(blur)

        # loop over the various dos files given
        for d in range(len(self.density_of_states)):
            # loop over the columns in each dos file
            for s in range(self.density_of_states[d].shape[1]):
                rho = self.density_of_states[d][:, s]
                energy = self.energy
                self.density_of_states[d][:, s][:] = smoother(
                    list(range(len(rho))), energy)

# plot density of states


def dos_plot(dos, *opt_list, **opt_dict): __dos_plot(plt, dos, *opt_list, **opt_dict)


def __dos_plot(figure, dos, *opt_list, **opt_dict):
    if isinstance(figure, types.ModuleType):
        figure = figure.gca()

    try:
        # new version of matplotlib
        grid_spec = figure.get_subplotspec()
        is_first_col = grid_spec.is_first_col()
        is_last_row = grid_spec.is_last_row()
    except BaseException:
        # old version of matplotlib
        is_first_col = figure.is_first_col()
        is_last_row = figure.is_last_row()

    offset = 0
    dos_max = 0
    dos_min = 0
    for d in range(len(dos.density_of_states)
                   ):  # loop over the various dos files given
        # loop over the columns in each dos file
        for s in range(dos.density_of_states[d].shape[1]):
            if dos_max < np.max(dos.density_of_states[d][:, s]):
                dos_max = np.max(dos.density_of_states[d][:, s])
            if dos_min > np.min(dos.density_of_states[d][:, s]):
                dos_min = np.min(dos.density_of_states[d][:, s])
            if dos.orientation == "vertical":
                figure.plot(dos.density_of_states[d][:, s],
                            dos.energy, label=dos.dos_dict[offset + s], color=dos.colors[offset + s], *opt_list, **opt_dict)
            elif dos.orientation == "horizontal":
                print("d = ", d, "s = ", s)
                figure.plot(
                    dos.energy, dos.density_of_states[d][:,
                                                         s], color=dos.colors[offset + s],
                    label=dos.dos_dict[offset + s], *opt_list, **opt_dict)
            else:
                raise ValueError(
                    f"The option {dos.orientation} is not a valid setting")
        offset += s + 1

    # decorate
    if dos.orientation == "vertical":
        if is_last_row:
            figure.set_xlabel(r'DOS (1/eV)')
        if is_first_col:
            figure.set_ylabel(r'$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)')

        figure.set_ylim(-10, 10)
        figure.axhline(0.0, color='k', lw=1, ls='dotted')
        if abs(dos_max) > abs(dos_min):
            figure.set_xlim(0, 1.05 * dos_max)
        else:
            figure.set_xlim(0.95 * dos_min, 1.05 * abs(dos_min))
            figure.axvline(0.0, color='k', lw=1, ls='dotted')

    elif dos.orientation == "horizontal":
        if is_last_row:
            figure.set_xlabel(r'$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)')
        if is_first_col:
            figure.set_ylabel(r'DOS (1/eV)')
        figure.set_xlim(-10, 10)
        figure.axvline(0.0, color='k', lw=1, ls='dotted')
        if abs(dos_max) > abs(dos_min):
            figure.set_ylim(0, 1.05 * dos_max)
        else:
            figure.set_ylim(0.95 * dos_min, 1.05 * abs(dos_min))
            figure.axhline(0.0, color='k', lw=1, ls='dotted')
    figure.legend(loc="best")
    figure.tick_params(axis='x', which='minor', length=3.5, width=0.5)


# dos_plot
mpl.axes.Axes.dos_plot = lambda self, dos, *opt_list, **opt_dict: __dos_plot(self, dos, *opt_list, **opt_dict)




