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

from . import w2kplot_base_style

# DensityOfStates object


class DensityOfStates:
    def __init__(self, filename) -> None:
        """
        Initialize the DensityOfStates object.

        Parameters
        ----------
        filename    : string, required
                     A Wien2k formatted dosXev(X/up/dn) or dossumev(X/up/dn)
        """
        self._filename = filename
        try:
            self._data = np.loadtxt(filename)
        except BaseException:
            raise FileNotFoundError(f"Could not find {filename}.")

    # dunder to get the underlying data;
    def __getitem__(self, x): return self._data.__getitem__(x)

    def _smooth_dos(self, blur):
        # implement a dos smoother
        pass


# alias for DensityOfStates
DOS = DensityOfStates

styleguides_str2int = {'line': 0,  # standard line plot
                       'fill': 1,  # fill the dos
                       'fill_line': 2,  # filled dos with solid line border
                       'grad_fill': 3   # gradient filled dos
                       }


def __dos_plot(figure, x, y, dos_style, *opt_list, **opt_dict):

    if isinstance(figure, types.ModuleType):
        figure = figure.gca()

    dos_style = styleguides_str2int[dos_style] if isinstance(
        dos_style, str) else dos_style

    label = opt_dict['label'] if 'label' in opt_dict else None
    color = opt_dict['color'] if 'color' in opt_dict else 'tab:blue'
    alpha = opt_dict['alpha'] if 'alpha' in opt_dict else 1

    lw = opt_dict['lw'] if 'lw' in opt_dict else 1
    lw = opt_dict['linewidth'] if 'linewidth' in opt_dict else lw
    ls = opt_dict['ls'] if 'ls' in opt_dict else '-'
    ls = opt_dict['linestyle'] if 'linestyle' in opt_dict else ls

    if dos_style == 0:
        figure.plot(x, y, *opt_list, **opt_dict)

    elif dos_style == 1:
        figure.fill_between(x, y, lw=0, color=color, alpha=alpha, label=None)
        figure.plot(x, y, lw=lw, color=color, ls=ls, alpha=alpha, label=label)

    elif dos_style == 2:
        figure.fill_between(x, y, lw=0, color=color, alpha=alpha, label=None)
        figure.plot(x, y, lw=lw, color=color, ls=ls, alpha=alpha, label=label)
        figure.plot(
            x,
            y,
            lw=lw + 1,
            color=color,
            ls=ls,
            alpha=alpha,
            label=None)
        figure.plot(x, y, lw=lw, color='k', ls=ls, label=None)

    elif dos_style == 3:
        raise NotImplementedError

    # try:
    #    # new version of matplotlib
    #    grid_spec = figure.get_subplotspec()
    #    is_first_col = grid_spec.is_first_col()
    #    is_last_row = grid_spec.is_last_row()
    # except BaseException:
    #    # old version of matplotlib
    #    is_first_col = figure.is_first_col()
    #    is_last_row = figure.is_last_row()

    figure.axvline(0.0, color='k', lw=1, ls='dotted')
    if max(y) < 0:
        figure.set_ylim(top=0)
    else:
        figure.set_ylim(bottom=0)

    # if min(x) < 0:
    #    #if is_last_row: figure.set_xlabel(r'$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)')
    # else:
    #    figure.axhline(0.0, color='k', lw=1, ls='dotted')
    #    if max(x) < 0: figure.set_ylim(top=0)
    #    else: figure.set_ylim(bottom=0)
    #    #if is_last_row: figure.set_ylabel(r'$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)')


# dos_plot
plt.style.use([w2kplot_base_style])


def dos_plot(x,
             y,
             dos_style=0,
             *opt_list,
             **opt_dict): __dos_plot(plt,
                                     x,
                                     y,
                                     dos_style,
                                     *opt_list,
                                     **opt_dict)


plt.style.use([w2kplot_base_style])
mpl.axes.Axes.dos_plot = lambda self, x, y, dos_style=0, * \
    opt_list, **opt_dict: __dos_plot(self, x, y, dos_style, *opt_list, **opt_dict)
