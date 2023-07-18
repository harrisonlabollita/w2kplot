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

from .structure import Structure

try:
    plt.style.use("w2kplot")
except BaseException:
    raise ImportError("Could not find install w2kplot style sheet!")


# Bands class
class Bands(object):
    def __init__(self,
                 case: str = None,
                 spaghetti: str = None,
                 klist_band: str = None,
                 eF_shift: float = 0) -> None:
        """
        Initialize the Bands w2kplot object.

        Parameters
        ----------
        spaghetti  : string, optional
                     Filename of case.spaghetti/up/dn_ene containing the εk information.
        klist_band : string, optional
                     Filename of case.klist_band containing the kpoint information, specifically,
                     the high symmetry points and high symmetry labels.
        eF_shift   : float, optional
                     Optional parameter to shift the Fermi energy. Units are eV.
        """
        self.spaghetti = case + '.spaghetti_ene' if case else spaghetti
        self.klist_band = case + '.klist_band' if case else klist_band
        self.eF_shift = eF_shift

        if self.spaghetti is None:
            try:
                self.spaghetti = glob.glob("*.spaghetti_ene")[0]
            except BaseException:
                raise FileNotFoundError(
                    "Could not find a case.spaghetti_ene file in this directory.\nPlease provide a case.spaghetti_ene file")

        if self.klist_band is None:
            try:
                self.klist_band = glob.glob("*.klist_band")[0]
            except BaseException:
                raise FileNotFoundError(
                    "Could not find a case.klist_band file in this directory.\nPlease provide a case.klist_band file")
        try:
            self.kpoints, self.Ek = self._get_dft_bands()
        except BaseException:
            raise Exception("Error in parsing bands!")
        try:
            self.high_symmetry_points, self.high_symmetry_labels = self._get_high_symmetry_path()
        except BaseException:
            raise Exception("Error in parsing klist_band file!")

    # methods for parsing the spaghetti_ene file and the klist_band file
    def _get_dft_bands(self):
        """
        Internal function to parse the provided case.spaghetti/up/dn_ene file.
        """
        try:
            f = open(self.spaghetti, "r")
            f.close()
        except BaseException:
            raise FileNotFoundError(
                "Could not find a case.spaghetti_ene file in this directory.\nPlease provide a case.spaghetti_ene file")
        try:
            f = open(self.klist_band, "r")
            f.close()
        except BaseException:
            raise FileNotFoundError(
                "Could not find a case.klist_band file in this directory\n. Please provide a valid case.klist_band file")

        skiprows = 0
        while True:
            try:
                data = np.loadtxt(
                    self.spaghetti, comments="bandindex", skiprows=skiprows)
                kpoints = np.unique(data[:, 3])
                Ek = data[:, 4].reshape(
                    int(len(data) / len(kpoints)), len(kpoints))
                break
            except BaseException:
                skiprows += 1
        return kpoints, Ek

    def _get_high_symmetry_path(self):
        """
        Internal function to parse the case.klist_band file for high symmetry points and
        high symmetry labels.
        """
        high_symmetry_points = []
        high_symmetry_labels = []
        f = open(self.klist_band)
        klist_band = f.readlines()
        f.close()
        try:
            for il, line in enumerate(klist_band):
                if line[:3] == "END":
                    break
                if line[:10].split():
                    high_symmetry_labels.append(
                        self._arg2latex(line.strip().split()[0]))
                    high_symmetry_points.append(il)
            high_symmetry_points = [self.kpoints[ind]
                                    for ind in high_symmetry_points]
        except BaseException:
            raise Exception(
                "An error occured when trying to parse the {} file".format(self.klist_band))

        return high_symmetry_points, high_symmetry_labels

    def _arg2latex(self, string: str) -> str:
        """
        Internal function to convert labels parsed from case.klist_band to
        LaTeX format.

        Parameters
        ----------
        string : string, required
                 Character from case.klist_band to be converted to LaTeX format.
        """
        special_chars = {'\\xG': r'$\Gamma$',
                         "GAMMA": r'$\Gamma$',
                         "LAMBDA": r"$\lambda$",
                         "DELTA": r"$\Delta$",
                         "SIGMA": r"$\Sigma$"}
        str_in_char = string in special_chars.keys()
        return special_chars[string] if str_in_char else string

    @staticmethod
    def Up(case=None, **kwargs):
        if case is None:
            try:
                spaghetti = glob.glob("*.spaghettiup_ene")[0]
            except BaseException:
                raise FileNotFoundError(
                    "Could not find a case.spaghettiup_ene file in this directory.\nPlease provide a case.spaghettiup_ene file")
            return Bands(spaghetti=spaghetti, **kwargs)
        else:
            return Bands(spaghetti=case + '.spaghettiup_ene',
                         klist_band=case + '.klist_band', **kwargs)

    @staticmethod
    def Down(case=None, **kwargs):
        if case is None:
            try:
                spaghetti = glob.glob("*.spaghettidn_ene")[0]
            except BaseException:
                raise FileNotFoundError(
                    "Could not find a case.spaghettidn_ene file in this directory.\nPlease provide a case.spaghetti_ene file")
            return Bands(spaghetti=spaghetti, **kwargs)
        else:
            return Bands(spaghetti=case + '.spaghettidn_ene',
                         klist_band=case + '.klist_band', **kwargs)
# bandstructure plotting


def __band_plot(figure, bands, *opt_list, **opt_dict):

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

    figure.tick_params(
        axis='both',
        which='minor',
        length=3.5,
        width=0.5,
        labelsize=12,
        bottom=False,
        top=False)
    figure.tick_params(
        axis='both',
        which='major',
        length=7,
        width=0.5,
        labelsize=12,
        bottom=False,
        top=False)

    # plot the the dispersion from the bands object
    for b in range(len(bands.Ek)):
        figure.plot(bands.kpoints,
                    bands.Ek[b, :] - bands.eF_shift, *opt_list, **opt_dict)

    # decorate the figure from here
    figure.set_xticks(bands.high_symmetry_points)
    if is_last_row:
        figure.set_xticklabels(bands.high_symmetry_labels)
    for k in bands.high_symmetry_points:
        figure.axvline(k, color="k", lw=1, ls='dotted')

    figure.axhline(0.0, color="k", ls='dotted', lw=1)
    if is_first_col:
        # if we are the first column we will always add the ylabel
        figure.set_ylabel(r"$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)")

    figure.set_ylim(-2, 2)
    figure.set_xlim(
        bands.high_symmetry_points[0], bands.high_symmetry_points[-1])


def band_plot(bands, *opt_list, **opt_dict): __band_plot(plt,
                                                         bands, *opt_list, **opt_dict)


# band_plot functionw;
mpl.axes.Axes.band_plot = lambda self, bands, * \
    opt_list, **opt_dict: __band_plot(self, bands, *opt_list, **opt_dict)


# FatBands class
class FatBands(Bands):
    def __init__(self,
                 atoms: List[int],
                 orbitals: List[List[int]],
                 colors: List[List[str]] = None,
                 weight: int = 80,
                 case: str = None,
                 spaghetti: str = None,
                 klist_band: str = None,
                 qtl: str = None,
                 eF: Union[str, float] = None,
                 struct: str = None,
                 eF_shift: float = 0) -> None:
        """
        Initialize the FatBand data object. This class is a child of the Bands class.

        Parameters
        ----------
        atoms       : list[int], required
                      List of atoms corresponding to the atoms in the case.struct file for which
                      the orbital character will be parsed and plotted.
        orbitals    : list[list[int]], required
                      a nested list where len(orbtials) == len(atoms). For atom, a list of orbitals for which
                      to plot the character of must be provided.
        colors      : list[list[string]], optional
                      a nested listed where len(colors) == len(atoms). For each atom, a list of colors should be provided
                      which corresponds to the color that will be given to the orbtial in the plot.
        weight      : int, optional
                      the weight to scale the orbital character by to enhance visualization.
                      The default value is 80
        spaghetti   : string, optional
                      Filename of case.spaghetti/up/dn_ene containing the εk information.
        klist_band  : string, optional
                      Filename of case.klist_band containing the kpoint information, specifically,
                      the high symmetry points and high symmetry labels.
        qtl         : string, optional
                      Filename of the case.qtl file which contains all of the information about the orbital
                      character of the bands.
        eF          : string or float, optional
                      The Fermi energy in Rydbergs. Needed to match the orbital weight to the band structure.
        struct      : string, optional
                      Filename of the case.struct file. Used to created a legend for the figure.
        eF_shit     : float, optional
                      Optional parameter to shift the Fermi energy. Units are eV.
        """
        super().__init__(case, spaghetti, klist_band, eF_shift)

        self.default_colors = [["dodgerblue", "lightcoral", "gold", "forestgreen", "magenta"],
                               ["b", "r", "g", "y", "c"],
                               ["royalblue", "salmon", "lawngreen", "orange", "deeppink"]]

        self.atoms = atoms
        self.orbitals = orbitals
        self.weight = weight
        self.colors = colors

        # modify file names if case is available
        struct = case + '.struct' if case else struct
        qtl = case + '.qtl' if case else qtl
        eF = case + '.scf' if case and not isinstance(eF, float) else eF

        assert len(self.atoms) == len(
            self.orbitals), f"list of atoms does not match list of orbitals: {len(atoms)} != {len(orbitals)}"

        if colors is None:
            self.colors = [[self.default_colors[ia % len(self.default_colors)][o % len(self.default_colors[0])]
                            for o in self.orbitals[ia]]
                           for (ia, a) in enumerate(self.atoms)]
        assert len(self.atoms) == len(
            self.colors), f"list of atoms does not match list of colors: {len(atoms)} != {len(colors)}"

        self.Ry2eV = 13.6          # convert from Ry (wien2k default) to eV
        self.qtl = qtl
        self.eF = eF
        self.structure = Structure(struct)

        if self.qtl is None:
            try:
                self.qtl = glob.glob("*.qtl")[0]
            except BaseException:
                raise FileNotFoundError(
                    "Could not find a case.qtl file in this directory. Please provide a case.qtl file")

        if self.eF is None:
            try:
                scf = open(glob.glob("*.scf")[0])
                self.eF = float([line for line in scf.readlines()
                                 if ":FER" in line][-1].split()[-1].strip())
                scf.close()
            except BaseException:
                raise FileNotFoundError("Could not find a case.scf file in this directory.\nThis file is needed to determine the Fermi energy.\
                                         You can instead simply provide this quantity upon initialization.")

        if isinstance(self.eF, str):
            scf = open(self.eF)
            self.eF = float([line for line in scf.readlines()
                             if ":FER" in line][-1].split()[-1].strip())
            scf.close()

        assert isinstance(
            self.eF, float), "Please provide the Fermi energy from the scf file or provide the scf file!"

    def _get_orbital_labels(self, atom: int, orbs: List[int]) -> List[str]:
        """
        convert the orbital labels in the case.qtl file into LaTeX format.

        Parameters
        ----------
        atom        : int, required
                      Index of atom from case.struct to get orbital labels for
        orbs        : list[int], required
                      list of orbitals to get the labels for. The indices correspond to the header of the case.qtl
                      for the atom provided under variable atom.
        Returns
        -------
        labels      : list[string]
                      converted orbital labels to LaTeX format.
        """
        qtl2orb = {"PZ": r"$p_{z}$",
                   "PX": r"$p_{x}$",
                   "PY": r"$p_{y}$",
                   "PX+PY": r"$p_{x}+p_{y}$",
                   "DZ2": r"$d_{z^{2}}$",
                   "DX2Y2": r"$d_{x^{2}-y^{2}}$",
                   "DXZ": r"$d_{xz}$",
                   "DYZ": r"$d_{yz}$",
                   "DXY": r"$d_{xy}$",
                   "DX2Y2+DXY": r"$d_{x^{2}-y^{2}}+d_{xy}$",
                   "DXZ+DYZ": r"$d_{xz}+d_{yz}$",
                   "0": "$s$",
                   "1": "$p$",
                   "2": "$d$",
                   "3": "$f$",
                   "tot": "Total",
                   }
        qtl_file = open(self.qtl)
        orbitals = [line for line in qtl_file.readlines() if "JATOM" in line]
        qtl_file.close()
        orbs_for_atom = orbitals[atom - 1].split()[-1].split(",")
        labels = [qtl2orb[orbs_for_atom[int(orbs[o]) - 1]]
                  for o in range(len(orbs))]
        return labels

    def create_legend(self):
        """
        internal function to build the legend elements for the figure legend.
        """
        legend_elements = []
        for (ia, a) in enumerate(self.atoms):
            labels = self._get_orbital_labels(a, self.orbitals[ia])
            for o in range(len(self.orbitals[ia])):
                legend_elements.append(Line2D([0], [0],
                                              linestyle='-',
                                              color=self.colors[ia][o],
                                              lw=2,
                                              # label=self.structure.atoms[a -
                                              # 1][0] + "-" + labels[o])
                                              label=self.structure[a - 1][0] + "-" + labels[o])
                                       )
        return legend_elements

# fatband plot functions


def fatband_plot(fat_bands,
                 *opt_list,
                 **opt_dict): __fatband_plot(plt,
                                             fat_bands,
                                             *opt_list,
                                             **opt_dict)


def __fatband_plot(figure, fat_bands, *opt_list, **opt_dict):
    if isinstance(figure, types.ModuleType):
        figure = figure.gca()

    # plot the bands
    __band_plot(figure, fat_bands, *opt_list, **opt_dict)

    qtl_file = open(fat_bands.qtl)
    qtl = qtl_file.readlines()
    qtl_file.close()
    start = [line + 1 for line in range(len(qtl)) if "BAND" in qtl[line]][0]
    qtl = qtl[start:]

    # plot the fatband character
    for (a, at) in enumerate(fat_bands.atoms):
        for o in range(len(fat_bands.orbitals[a])):
            E, character = [], []
            for line in qtl:
                if 'BAND' not in line:
                    if line.split()[1] == str(at):
                        # wien2k interal units are Ry switch to eV
                        E.append(
                            (float(
                                line.split()[0]) -
                                fat_bands.eF) *
                            fat_bands.Ry2eV -
                            fat_bands.eF_shift)
                        # weight factor
                        enh = float(fat_bands.weight *
                                    fat_bands.structure.atoms[at - 1][1])
                        # qtl overlap
                        ovlap = (
                            float(line.split()[int(fat_bands.orbitals[a][o]) + 1]))
                        character.append(enh * ovlap)
                else:
                    assert len(fat_bands.kpoints) == len(
                        E), f"Did not parse file correctly! {len(fat_bands.kpoints), len(E)}"
                    assert len(E) == len(
                        character), "Did not parse file correctly!"
                    figure.scatter(
                        fat_bands.kpoints,
                        E,
                        character,
                        fat_bands.colors[a][o],
                        rasterized=True)
                    E, character = [], []


# fatband_plot
mpl.axes.Axes.fatband_plot = lambda self, fat_bands, * \
    opt_list, **opt_dict: __fatband_plot(self, fat_bands, *opt_list, **opt_dict)
