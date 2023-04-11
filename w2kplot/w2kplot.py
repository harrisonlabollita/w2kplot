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

import sys
import glob
import os
import importlib
import shutil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.lines import Line2D
import types
from typing import Union, List, Dict

try:
    plt.style.use("w2kplot")
except BaseException:
    raise ImportError("Could not find install w2kplot style sheet!")


class Structure(object):
    """this is a wien2k structure class that contains the information
       we need about about the crystal structure to plot the bands.
    """

    def __init__(self, filename: str) -> None:
        """
        Initialize the structure class. This is used to contain information
        about the crystal structure store in filename.
        This class is intended to only be used internally by w2kplot.

        Parameters
        ----------
        filename : string, optional
                   Filename of case.struct. If not given glob.glob will search current directory
                   for file with extension .struct.
        """
        if filename is None:
            try:
                self.load()
            except BaseException:
                raise FileNotFoundError(
                    "Couldn't find a case.struct file in this directory!")
        else:
            self.load(filename=filename)

    def load(self, filename: str = None) -> None:
        """
        Function to parse struct file and store the data into the Structure class

        Parameters
        ----------
        filename : string, optional
                   Filename of case.struct. If not given glob.glob will search current directory
                   for file with extension .struct.
        """
        if filename is None:
            struct_file = open(glob.glob("*.struct")[0])
            contents = struct_file.readlines()
            struct_file.close()
        else:
            f = open(filename)
            contents = f.readlines()
            f.close()

        try:  # does this try/except handle all cases
            self.nat = int(contents[1].split()[2])
            self.spg = int(contents[1].split()[3])
        except BaseException:
            self.nat = int(contents[1].split()[1])
            self.spg = int(contents[1].split()[2])

        iatom = list(range(1, self.nat + 1))
        mults = [int(line.split("=")[1].split()[0])
                 for line in contents if "MULT" in line]
        specs = [str(line.split()[0]) for line in contents if "NPT" in line]
        self.atoms = {}
        assert len(mults) == len(
            specs), "The struct file was not parsed correctly!"
        assert len(iatom) == len(
            specs), "The struct file was not parsed correctly!"
        for a in range(self.nat):
            self.atoms[a] = [specs[a], mults[a]]
        # load the symmetries in the structure here as well.
        # store them in self.symmetries


class Bands(object):
    def __init__(self, case: str = None,
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
            self.kpoints, self.Ek = self.get_dft_bands()
            self.high_symmetry_points, self.high_symmetry_labels = self.get_high_symmetry_path()
        except BaseException:
            raise Exception("please contact the developer with your issue!")

    # methods for parsing the spaghetti_ene file and the klist_band file
    def get_dft_bands(self):
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

    def get_high_symmetry_path(self):
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
                        self.arg2latex(line.strip().split()[0]))
                    high_symmetry_points.append(il)
            high_symmetry_points = [self.kpoints[ind]
                                    for ind in high_symmetry_points]
        except BaseException:
            raise Exception(
                "An error occured when trying to parse the {} file".format(self.klist_band))

        return high_symmetry_points, high_symmetry_labels

    def arg2latex(self, string: str) -> str:
        """
        Internal function to convert labels parsed from case.klist_band to
        LaTeX format.

        Parameters
        ----------
        string : string, required
                 Character from case.klist_band to be converted to LaTeX format.
        """
        if string == '\\xG':
            return r'$\Gamma$'
        elif string == "GAMMA":
            return r'$\Gamma$'
        elif string == "LAMBDA":
            return r"$\lambda$"
        elif string == "DELTA":
            return r"$\Delta$"
        elif string == "SIGMA":
            return r"$\Sigma$"
        else:
            return string

# plot bandstructure


def band_plot(bands, *opt_list, **opt_dict):
    __band_plot(plt, bands, *opt_list, **opt_dict)


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

    # plot the the dispersion from the bands object
    for b in range(len(bands.Ek)):
        figure.plot(bands.kpoints,
                    bands.Ek[b, :] - bands.eF_shift, *opt_list, **opt_dict)

    # decorate the figure from here
    figure.set_xticks(bands.high_symmetry_points)
    if is_last_row:
        figure.set_xticklabels(bands.high_symmetry_labels)
    for k in bands.high_symmetry_points:
        figure.axvline(k, color="k", lw=1)

    figure.axhline(0.0, color="k", ls='dotted', lw=1)
    if is_first_col:
        # if we are the first column we will always add the ylabel
        figure.set_ylabel(r"$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)")

    figure.set_ylim(-2, 2)
    figure.set_xlim(
        bands.high_symmetry_points[0], bands.high_symmetry_points[-1])


# band_plot
mpl.axes.Axes.band_plot = lambda self, bands, * \
    opt_list, **opt_dict: __band_plot(self, bands, *opt_list, **opt_dict)


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

    def get_orbital_labels(self, atom: int, orbs: List[int]) -> List[str]:
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
            labels = self.get_orbital_labels(a, self.orbitals[ia])
            for o in range(len(self.orbitals[ia])):
                legend_elements.append(Line2D([0], [0],
                                              linestyle='-',
                                              color=self.colors[ia][o],
                                              lw=3,
                                              label=self.structure.atoms[a - 1][0] + "-" + labels[o]))
        return legend_elements


# plot fatbands
def fatband_plot(fat_bands, *opt_list, **opt_dict):
    __fatband_plot(plt, fat_bands, *opt_list, **opt_dict)


def __fatband_plot(figure, fat_bands, *opt_list, **opt_dict):
    if isinstance(figure, types.ModuleType):
        figure = figure.gca()

    # plot the bands
    __band_plot(figure, fat_bands, *opt_list, **opt_dict)

    # plot the fatband character
    for (a, at) in enumerate(fat_bands.atoms):
        for o in range(len(fat_bands.orbitals[a])):
            qtl_file = open(fat_bands.qtl)
            qtl = qtl_file.readlines()
            qtl_file.close()
            start = [
                line + 1 for line in range(len(qtl)) if "BAND" in qtl[line]][0]
            qtl = qtl[start:]
            E = []
            character = []
            for line in qtl:
                if 'BAND' not in line:
                    if line.split()[1] == str(at):
                        # wien2k interal units are Ry switch to eV
                        E.append(
                            (float(line.split()[0]) - fat_bands.eF) * fat_bands.Ry2eV - fat_bands.eF_shift)
                        # weight factor
                        enh = float(fat_bands.weight *
                                    fat_bands.structure.atoms[at - 1][1])
                        # qtl overlap
                        ovlap = (
                            float(line.split()[int(fat_bands.orbitals[a][o]) + 1]))
                        character.append(enh * ovlap)
                else:
                    assert len(fat_bands.kpoints) == len(
                        E), "Did not parse file correctly!"
                    assert len(E) == len(
                        character), "Did not parse file correctly!"
                    figure.scatter(fat_bands.kpoints, E, character,
                                   fat_bands.colors[a][o], rasterized=True)
                    E = []
                    character = []


# fatband_plot
mpl.axes.Axes.fatband_plot = lambda self, fat_bands, * \
    opt_list, **opt_dict: __fatband_plot(self, fat_bands, *opt_list, **opt_dict)


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


def dos_plot(dos, *opt_list, **opt_dict):
    __dos_plot(plt, dos, *opt_list, **opt_dict)


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
mpl.axes.Axes.dos_plot = lambda self, dos, * \
    opt_list, **opt_dict: __dos_plot(self, dos, *opt_list, **opt_dict)


class WannierBands(object):
    # TODO: would it be possible to get high-symmetry points
    # for just a Wannier band plot?
    def __init__(self, wann_bands: str = None) -> None:
        """
        Initialze the WannierBands object.

        Parameters
        ----------
        wann_bands  : string, optional
                      Filename of Wannier90 *_band.dat file.
        """
        self.wann_bands = wann_bands

        if self.wann_bands is None:
            try:
                self.wann_bands = glob.glob("*_band.dat")[0]
            except BaseException:
                raise FileNotFoundError(
                    "Could not find a case_band.dat file in this directory\n. Please provide a case_band.dat file!")

        self.kpts, self.wann_bands = self.get_wannier_bands()

    def get_wannier_bands(self):
        """
        internal function for parsing the Wannier90 band.dat file.
        """
        data = np.loadtxt(self.wann_bands)
        kpts = np.unique(data[:, 0]) * 0.53  # convert units!
        wann_bands = data[:, 1].reshape(int(len(data) / len(kpts)), len(kpts))
        return kpts, wann_bands


# plot wannier90 bands compared to DFT bands
def wannier_band_plot(wannier_bands, *opt_list, **opt_dict):
    __wannier_band_plot(plt, wannier_bands, *opt_list, **opt_dict)


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


mpl.axes.Axes.wannier_band_plot = lambda self, wannier_bands, * \
    opt_list, **opt_dict: __wannier_band_plot(self, wannier_bands, *opt_list, **opt_dict)


class FermiSurface(object):
    def __init__(self, energy=None, struct=None):

        self.energy = energy
        self.struct = Structure(struct)

        if self.energy is None:
            try:
                self.energy = glob.glob("*.energy")[0]
            except BaseException:
                raise FileNotFoundError(
                    "Could not find a case.energy file in this directory.\nPlease provide a case.energy file")

        def get_fermi_surface(self):
            # from case.energy get kpts and energies
            # interpolate data using griddata
            # return kx, ky grid and surf grid to be plotted
            raise NotImplementedError(
                "This function has not been implemented yet!")
# plot fermi surface
# def fermi_surface_plot(fermi_surface):
#    __fermi_surface_plot(plt, fermi_surface)

# def __fermi_surface_plot(figure, fermi_surface):
#    if isinstance(figure, types.ModuleType): figure = figure.gca()

#mpl.axes.Axes.fermi_surface_plot = lambda self, fermi_surface, *opt_list, **opt_dict : __fermi_surface_plot(self, fermi_surface, *opt_list, **opt_dict)


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


mpl.axes.Axes.charge_2d_plot = lambda self, charge_density, * \
    opt_list, **opt_dict: __charge_2d_plot(self, charge_density, *opt_list, **opt_dict)
