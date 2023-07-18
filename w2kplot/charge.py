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

class ChargeDensity(object):
    def __init__(self, case=None, rho=None, transform=lambda x: x):

        rho = case + '.rho' if case else rho

        self.rho = rho
        assert callable(transform), "The transform function must be callable!"

        self.transform = transform
        if self.rho is None:
            try:
                self.rho = glob.glob("*.rho")[0]
            except Exception:
                raise FileNotFoundError(
                    "Could not find a case.rho file in this repository.\nPlease provide a case.rho file")
        if isinstance(self.rho, str):
            self.rho = self.get_charge_density()

    def __sub__(self, other_rho):
        assert self.rho.shape == other_rho.rho.shape
        return ChargeDensity(rho=self.rho - other_rho.rho)

    def __add__(self, other_rho):
        assert self.rho.shape == other_rho.rho.shape
        return ChargeDensity(rho=self.rho + other_rho.rho)

    def get_charge_density(self):
        f = open(self.rho)
        data = f.readlines()
        f.close()
        Nx, Ny = list(map(int, data[0].split()[:2]))
        charge = []
        for i in range(1, len(data)):
            charge.extend(list(map(float, data[i].split())))
        charge = np.array(charge).reshape(Nx, Ny)
        return self.transform(charge)


def charge_2d_plot(charge_density, *opt_list, **opt_dict):
    __charge_2d_plot(plt, charge_density, *opt_list, **opt_dict)


def __charge_2d_plot(figure, charge_density, *opt_list, **opt_dict):
    if isinstance(figure, types.ModuleType):
        figure = figure.gca()

    # plot the charge density
    figure.imshow(charge_density.rho, *opt_list, **opt_dict)

    # decorate the figure from here
    figure.axis('off')

plt.style.use([w2kplot_base_style])
mpl.axes.Axes.charge_2d_plot = lambda self, charge_density, *opt_list, **opt_dict: __charge_2d_plot(self, charge_density, *opt_list, **opt_dict)
