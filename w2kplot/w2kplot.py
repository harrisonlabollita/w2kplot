# -*- coding: utf-8 -*-

################################################################################
#
# w2kplot: a thin Python wrapper around matplotlib
#
# Copyright (C) 2022 Harrison LaBollita
# Authors: H. LaBollita
#
# w2kplot is free software licensed under the terms of the MIT license.
#
################################################################################

import sys
import glob
import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.lines import Line2D
import types

def install_style_sheet(matplotlib_file):
    sheet = ["# Matplotlib style for w2kplot figures",
             "# set x axis",
             "xtick.direction : in",
             "xtick.major.size : 7",
             "xtick.major.width : 0.5",
             "xtick.minor.size : 3.5",
             "xtick.minor.width : 0.5",
             "xtick.minor.visible : False",
             "xtick.top : True",
             "xtick.labelsize : 15",
             "# set y axis",
             "ytick.direction : in",
             "ytick.major.size : 7",
             "ytick.major.width : 0.5",
             "ytick.minor.size : 3.5",
             "ytick.minor.width : 0.5",
             "ytick.minor.visible : True",
             "ytick.right : True",
             "ytick.labelsize : 15",
             "# set line widths",
             "axes.linewidth : 0.5",
             "axes.labelsize : 15",
             "lines.linewidth : 0.5",
             "legend.frameon : False",
             "savefig.bbox : tight",
             "savefig.pad_inches : 0.05",
             "font.sans-serif : Arial",
             "font.family : sans-serif"
             ]
    location = os.path.dirname(matplotlib_file) + "/mpl-data/stylelib/"
    print("[INFO] installing w2kplot's matplotlib style sheet: %s" %(location))
    with open(location + "w2kplot.mplstyle", "w") as f: f.write("\n".join(sheet))

if "w2kplot" not in plt.style.available:
    print("[WARNING] Custom matplotlib style sheet not found!")
    print("Installing style sheet")
    install_style_sheet(plt.__file__)
plt.style.use("w2kplot")




class Error(Exception):
    """Base class for other exceptions"""
    pass


class ParseSpaghettiError(Error):
    """Raised when there is an error parsing the case.spaghetti_ene file."""
    pass

class ParseKlistBandError(Error):
    """Raised when there is an error parsing the case.klist_band file."""
    pass

class Structure(object):
    """this is a wien2k structure class that contains the information 
       we need about about the crystal structure to plot the bands.
    """
    def __init__(self, filename):
        if filename is None:
            try:
                self.load()
            except FileNotFoundError :
                print("Couldn't find a case.struct file in this directory!")
        else:
            self.load(filename=filename)

    def load(self, filename=None):
        if filename is None:
            contents=open(glob.glob("*.struct")[0]).readlines()
        else:
            contents=open(filename).readlines()

        try: # does this try/except handle all cases
            self.nat=int(contents[1].split()[2])
            self.spg=int(contents[1].split()[3])
        except:
            self.nat=int(contents[1].split()[1])
            self.spg=int(contents[1].split()[2])

        iatom=list(range(1,self.nat+1))
        mults=[int(line.split("=")[1].split()[0]) for line in contents if "MULT" in line]
        specs=[str(line.split()[0]) for line in contents if "NPT" in line]
        self.atoms={}
        assert len(mults)==len(specs), "The struct file was not parsed correctly!"
        assert len(iatom)==len(specs), "The struct file was not parsed correctly!"
        for a in range(self.nat): self.atoms[a]=[specs[a], mults[a]]

class Bands(object):
    def __init__(self, spaghetti=None, klist_band=None):
        self.spaghetti = spaghetti
        self.klist_band = klist_band
        if self.spaghetti is None:
            try:
                self.spaghetti = glob.glob("*.spaghetti_ene")[0]
            except FileNotFoundError:
                print("Could not find a case.spaghetti_ene file in this directory\n. Please provide a case.spaghetti_ene file")
        if self.klist_band is None:
            try:
                self.klist_band = glob.glob("*.klist_band")[0]
            except FileNotFoundError:
                print("Could not find a case.klist_band file in this directory\n. Please provide a case.klist_band file")

        self.kpoints, self.Ek = self.grab_bands()
        self.high_symmetry_points, self.high_symmetry_labels = self.grab_high_symmetry_path()
    

    # methods for parsing the spaghetti_ene file and the klist_band file
    def grab_bands(self):
        try:
            data = np.loadtxt(self.spaghetti, comments="bandindex")
            kpoints = np.unique(data[:,3])
            Ek      = data[:,4].reshape(int(len(data)/len(kpoints)), len(kpoints))
        except ParseSpaghettiError:
            print("An error occured when trying to parse the {} file".format(self.spaghetti))
        return kpoints, Ek

    
    def grab_high_symmetry_path(self):
        high_symmetry_points = []
        high_symmetry_labels = []
        
        klist_band = open(self.klist_band).readlines()
        try:
            for il, line in enumerate(klist_band):
                if line[:3] == "END": break
                if line[:10].split():
                    high_symmetry_labels.append(self.arg2latex(line.strip().split()[0]))
                    high_symmetry_points.append(il)
            high_symmetry_points = [self.kpoints[ind] for ind in high_symmetry_points]

        except ParseKlistBandError:
            print("An error occured when trying to parse the {} file".format(self.klist_band))

        return high_symmetry_points, high_symmetry_labels
    
    def arg2latex(self, string):
        if string == '\\xG':
            return '$\Gamma$'
        elif string == "GAMMA":
            return '$\Gamma$'
        elif  string == "LAMBDA":
            return "$\lambda$"
        elif  string == "DELTA":
            return "$\Delta$"
        elif  string == "SIGMA":
            return "$\Sigma$"
        else:
            return string


class FatBands(Bands):
    def __init__(self, atoms, orbitals, colors=None, weight=80, spaghetti=None, klist_band=None, qtl=None, eF=None, struct=None):
        super().__init__(spaghetti, klist_band)

        self.default_colors = [["dodgerblue", "lightcoral", "gold", "forestgreen", "magenta"],
                               ["b", "r", "g", "y", "c"],
                               ["royalblue", "salmon", "lawngreen", "orange", "deeppink"]]

        self.atoms = atoms
        self.orbitals = orbitals
        self.weight = weight
        self.colors = colors

        if colors is None:
            self.colors = [[self.default_colors[ia%len(self.default_colors)][o%len(self.default_colors[0])]  \
                           for o in self.orbitals[ia]]  \
                           for (ia, a) in enumerate(self.atoms)]

        self.Ry2eV = 13.6          # convert from Ry (wien2k default) to eV
        self.qtl    = qtl
        self.eF     = eF
        self.structure = Structure(struct)

        if self.qtl is None:
            try:
                self.qtl = glob.glob("*.qtl")[0]
            except FileNotFoundError:
                print("Could not find a case.qtl file in this directory. Please provide a case.qtl file")

        if self.eF is None:
            try:
                scf = glob.glob("*.scf")[0]
                self.eF = float([line for line in open(scf).readlines() if ":FER" in line][-1].split()[-1].strip())
            except FileNotFoundError:
                print("Could not find a case.scf file in this directory\n. This file is needed to determine the Fermi energy. \
                       You can instead simply provide this quantity upon initialization.")
                

    def grab_orbital_labels(self, atom, orbs):
        """grabs the labels of the fatbands plotted from the qtl file and returns an array labels."""
        qtl2orb = {    "PZ"        : r"$p_{z}$",
                       "PX"        : r"$p_{x}$",
                       "PY"        : r"$p_{y}$",
                       "PX+PY"     : r"$p_{x}+p_{y}$",
                       "DZ2"       : r"$d_{z^{2}}$",
                       "DX2Y2"     : r"$d_{x^{2}-y^{2}}$",
                       "DXZ"       : r"$d_{xz}$",
                       "DYZ"       : r"$d_{yz}$",
                       "DXY"       : r"$d_{xy}$",
                       "DX2Y2+DXY" : r"$d_{x^{2}-y^{2}}+d_{xy}$",
                       "DXZ+DYZ"   : r"$d_{xz}+d_{yz}$",
                       "0"         : "$s$",
                       "1"         : "$p$",
                       "2"         : "$d$",
                       "3"         : "$f$",
                       "tot"       : "Total",
                  }
        orbitals=[line for line in open(self.qtl).readlines() if "JATOM" in line] 
        orbs_for_atom = orbitals[atom-1].split()[-1].split(",")
        labels = [ qtl2orb[orbs_for_atom[int(orbs[o])-1]] for o in range(len(orbs))] 
        return labels
    
    def create_legend(self):
        legend_elements = []
        for (ia, a) in enumerate(self.atoms):
            labels=self.grab_orbital_labels(a, self.orbitals[ia])
            for o in range(len(self.orbitals[ia])):
                legend_elements.append(Line2D([0], [0], 
                                       linestyle= '-', 
                                       color=self.colors[ia][o], 
                                       lw=3, 
                                       label=self.structure.atoms[a-1][0]+"-"+labels[o]))
        return legend_elements


class DensityOfStates(object):
    def __init__(self, dos=None, dos_dict=None):
        self.dos = dos
        self.dos_dict = dos_dict

        if self.dos is None:
            try:
                self.dos = glob.glob("*.dos*")
                print("Found {} density of states files".format(len(self.dos)))
            except FileNotFoundError:
                print("Could not find any files matching case.dosXev, where X is a number")
        
        if self.dos_dict is None:
            # if a dictionary mapping each column to a name is not provided we will build one
            self.dos_dict = {}
            offset = 0
            for file in self.dos:
                headers=open(file).readlines()[2].split()[2:] # skips the # and ENERGY
                for h in range(len(headers)):
                    self.dos_dict[h+offset] = headers[h]
                offset += len(headers)

        self.energy, self.density_of_states = self.grab_dos()

    def grab_dos(self):
        density_of_states = []
        for file in self.dos:
            data = np.loadtxt(file, comments='#')
            energy = data[:,0]
            density_of_states.append(np.loadtxt(file, comments="#")[:,2:])
        return energy, density_of_states

    def smooth_dos(self, fwhm):
        """smooths out the density of states. Mainly for aesthetics"""
        
        def fwhm2sigma(fwhm):
            return fwhm / np.sqrt(8 * np.log(2))

        def blur(ie, e):
            kernel=np.exp(-(energy-e)**2/(2*sigma**2))
            kernel/=np.sum(kernel) # normalize
            return np.sum(rho*kernel)

        sigma = fwhm2sigma(fwhm)
        smoother = np.vectorize(blur)

        for d in range(len(self.density_of_states)): # loop over the various dos files given
            for s in range(self.density_of_states[d].shape[1]): # loop over the columns in each dos file
                rho = self.density_of_states[d][:,s]
                energy=self.energy
                self.density_of_states[d][:,s][:] = smoother(list(range(len(rho))), energy)

class FermiSurface(object):
    def __init__(self):
        print("not implemented yet")
        pass

# plotting methods

# plot bandstructure
def band_plot(bands, *opt_list, **opt_dict):
    __band_plot(plt, bands, *opt_list, **opt_dict)

def __band_plot(figure, bands, *opt_list, **opt_dict):
    
    if isinstance(figure, types.ModuleType): figure = figure.gca()
            

    # plot the the dispersion from the bands object
    for b in range(len(bands.Ek)): figure.plot(bands.kpoints, bands.Ek[b,:], *opt_list, **opt_dict)


    # decorate the figure from here
    figure.set_xticks(bands.high_symmetry_points)
    figure.set_xticklabels(bands.high_symmetry_labels)
    for k in bands.high_symmetry_points: figure.axvline(k, color="k", lw=1)
    figure.axhline(0.0, color="k", lw=1)
    figure.set_ylabel(r"$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)")
    figure.set_ylim(-2, 2); 
    figure.set_xlim(bands.high_symmetry_points[0], bands.high_symmetry_points[-1]);

mpl.axes.Axes.band_plot = lambda self, bands, *opt_list, **opt_dict : __band_plot(self, bands, *opt_list, **opt_dict)

# plot fatbands
def fatband_plot(fat_bands, *opt_list, **opt_dict):
    __fatband_plot(plt, fat_bands, *opt_list, **opt_dict)


def __fatband_plot(figure, fat_bands, *opt_list, **opt_dict):
    if isinstance(figure, types.ModuleType): figure = figure.gca()

    # plot the bands 
    __band_plot(figure, fat_bands, *opt_list, **opt_dict)
    
    # plot the fatband character
    for (a, at) in enumerate(fat_bands.atoms):
        for o in range(len(fat_bands.orbitals[a])):
            qtl           = open(fat_bands.qtl).readlines() 
            start         = [line+1 for line in range(len(qtl)) if "BAND" in qtl[line]][0]
            qtl           = qtl[start:]
            E         = []
            character = []
            for line in qtl:
                if 'BAND' not in line:
                    if line.split()[1] == str(at):
                        E.append((float(line.split()[0]) - fat_bands.eF)*fat_bands.Ry2eV)    # wien2k interal units are Ry switch to eV
                        enh   = float(fat_bands.weight*fat_bands.structure.atoms[at-1][1])   # weight factor
                        ovlap = (float(line.split()[int(fat_bands.orbitals[a][o]) + 1]))     # qtl overlap
                        character.append(enh*ovlap)
                else:
                    assert len(fat_bands.kpoints) == len(E), "Did not parse file correctly!"
                    assert len(E) == len(character),         "Did not parse file correctly!"
                    figure.scatter(fat_bands.kpoints, E, character, fat_bands.colors[a][o], rasterized=True)
                    E = []
                    character = []

mpl.axes.Axes.fatband_plot = lambda self, fat_bands, *opt_list, **opt_dict : __fatband_plot(self, fat_bands, *opt_list, **opt_dict)
                


# plot density of states
def dos_plot(dos, *opt_list, **opt_dict):
    __dos_plot(plt, dos, *opt_list, **opt_dict)


def __dos_plot(figure, dos, *opt_list, **opt_dict):
    if isinstance(figure, types.ModuleType): figure = figure.gca()
    
    offset = 0
    dos_max = 0
    for d in range(len(dos.density_of_states)): # loop over the various dos files given
        for s in range(dos.density_of_states[d].shape[1]): # loop over the columns in each dos file
            if dos_max < np.max(dos.density_of_states[d][:,s]):
                dos_max = np.max(dos.density_of_states[d][:,s])
            figure.plot(dos.energy, dos.density_of_states[d][:,s], label=dos.dos_dict[offset+s], *opt_list, **opt_dict)
        offset += s

    # decorate
    figure.set_xlabel(r'$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)')
    figure.set_ylabel(r'DOS (1/eV)')
    figure.set_xlim(-10, 10)
    figure.set_ylim(0, 1.05*dos_max)
    figure.axvline(0.0, color='k', lw=1, ls='dotted')
    figure.legend(loc="best")


mpl.axes.Axes.dos_plot = lambda self, dos, *opt_list, **opt_dict : __dos_plot(self, dos, *opt_list, **opt_dict)


# plot fermi surface
#def fermi_surface_plot(fermi_surface):
#    __fermi_surface_plot(plt, dos)

#def __fermi_surface_plot(figure, fermi_surface):
#    if isinstance(figure, types.ModuleType): figure = figure.gca()

#mpl.axes.Axes.fermi_surface_plot = lambda self, dos : __fermi_surface_plot(self, fermi_surface)
