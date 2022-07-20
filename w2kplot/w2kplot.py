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
import importlib
import shutil
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.lines import Line2D
import types

try:
    plt.style.use("w2kplot")
except:
    raise ImportError("Could not find install w2kplot style sheet!")

class Structure(object):
    """this is a wien2k structure class that contains the information 
       we need about about the crystal structure to plot the bands.
    """
    def __init__(self, filename):
        if filename is None:
            try:
                self.load()
            except: 
                raise FileNotFoundError("Couldn't find a case.struct file in this directory!")
        else:
            self.load(filename=filename)

    def load(self, filename=None):
        if filename is None:
            struct_file = open(glob.glob("*.struct")[0])
            contents = struct_file.readlines(); struct_file.close()
        else:
            f = open(filename)
            contents=f.readlines(); f.close()

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
        # load the symmetries in the structure here as well.
        # store them in self.symmetries

class Bands(object):
    def __init__(self, spaghetti=None, klist_band=None, eF_shift=0):
        self.spaghetti = spaghetti
        self.klist_band = klist_band
        self.eF_shift   = eF_shift

        if self.spaghetti is None:
            try:
                self.spaghetti = glob.glob("*.spaghetti_ene")[0]
            except:
                raise FileNotFoundError("Could not find a case.spaghetti_ene file in this directory.\nPlease provide a case.spaghetti_ene file")

        if self.klist_band is None:
            try:
                self.klist_band = glob.glob("*.klist_band")[0]
            except:
                raise FileNotFoundError("Could not find a case.klist_band file in this directory.\nPlease provide a case.klist_band file")
        try:
            self.kpoints, self.Ek = self.get_dft_bands()
            self.high_symmetry_points, self.high_symmetry_labels = self.get_high_symmetry_path()
        except: 
            raise Exception("please contact the developer with your issue!")

    # methods for parsing the spaghetti_ene file and the klist_band file
    def get_dft_bands(self):
        # first check if the file name given is good, if not return error
        try:
            f=open(self.spaghetti,"r"); f.close()
        except:
            raise FileNotFoundError("Could not find a case.spaghetti_ene file in this directory.\nPlease provide a case.spaghetti_ene file")
        try:
            f=open(self.klist_band,"r"); f.close()
        except: 
            raise FileNotFoundError("Could not find a case.klist_band file in this directory\n. Please provide a valid case.klist_band file")

        skiprows = 0
        while True:
            try:
                data = np.loadtxt(self.spaghetti, comments="bandindex", skiprows=skiprows)
                kpoints = np.unique(data[:,3])
                Ek      = data[:,4].reshape(int(len(data)/len(kpoints)), len(kpoints))
                break
            except:
                skiprows += 1
        return kpoints, Ek
    
    def get_high_symmetry_path(self):
        high_symmetry_points = []
        high_symmetry_labels = []
        f = open(self.klist_band) 
        klist_band = f.readlines()
        f.close()
        try:
            for il, line in enumerate(klist_band):
                if line[:3] == "END": break
                if line[:10].split():
                    high_symmetry_labels.append(self.arg2latex(line.strip().split()[0]))
                    high_symmetry_points.append(il)
            high_symmetry_points = [self.kpoints[ind] for ind in high_symmetry_points]
        except:
            raise Exception("An error occured when trying to parse the {} file".format(self.klist_band))

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
    def __init__(self, atoms, orbitals, colors=None, weight=80, spaghetti=None, klist_band=None, qtl=None, eF=None, struct=None, eF_shift=0):
        super().__init__(spaghetti, klist_band, eF_shift)

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
            except: 
                raise FileNotFoundError("Could not find a case.qtl file in this directory. Please provide a case.qtl file")

        if self.eF is None:
            try:
                scf = open(glob.glob("*.scf")[0])
                self.eF = float([line for line in scf.readlines() if ":FER" in line][-1].split()[-1].strip())
                scf.close()
            except: 
                raise FileNotFoundError("Could not find a case.scf file in this directory.\nThis file is needed to determine the Fermi energy. \
                       You can instead simply provide this quantity upon initialization.")

        if isinstance(self.eF, str): 
            scf = open(self.eF)
            self.eF = float([line for line in scf.readlines() if ":FER" in line][-1].split()[-1].strip())
            scf.close()

        assert isinstance(self.eF, float), "Please provide the Fermi energy from the scf file or provide the scf file!"

                

    def get_orbital_labels(self, atom, orbs):
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
        qtl_file = open(self.qtl)
        orbitals=[line for line in qtl_file.readlines() if "JATOM" in line]; qtl_file.close()
        orbs_for_atom = orbitals[atom-1].split()[-1].split(",")
        labels = [ qtl2orb[orbs_for_atom[int(orbs[o])-1]] for o in range(len(orbs))] 
        return labels
    
    def create_legend(self):
        legend_elements = []
        for (ia, a) in enumerate(self.atoms):
            labels=self.get_orbital_labels(a, self.orbitals[ia])
            for o in range(len(self.orbitals[ia])):
                legend_elements.append(Line2D([0], [0], 
                                       linestyle= '-', 
                                       color=self.colors[ia][o], 
                                       lw=3, 
                                       label=self.structure.atoms[a-1][0]+"-"+labels[o]))
        return legend_elements

class WannierBands(object):
    def __init__(self, wann_bands=None):
        self.wann_bands = wann_bands

        if self.wann_bands is None:
            try:
                self.wann_bands = glob.glob("*_band.dat")[0]
            except: 
                raise FileNotFoundError("Could not find a case_band.dat file in this directory\n. Please provide a case_band.dat file!")

        self.kpts, self.wann_bands = self.get_wannier_bands()


    def get_wannier_bands(self):
        data = np.loadtxt(self.wann_bands)
        kpts = np.unique(data[:,0]) * 0.53 # convert units!
        wann_bands = data[:,1].reshape(int(len(data)/len(kpts)), len(kpts))
        return  kpts, wann_bands



class DensityOfStates(object):
    def __init__(self, dos=None, dos_dict=None):
        self.dos = dos
        self.dos_dict = dos_dict

        if self.dos is None:
            try:
                self.dos = glob.glob("*.dos*")
                # For debugging
                #print("Found {} density of states files".format(len(self.dos)))
            except:
                raise FileNotFoundError("Could not find any files matching case.dosXev, where X is a number")
        
        if self.dos_dict is None:
            # if a dictionary mapping each column to a name is not provided we will build one
            self.dos_dict = {}
            offset = 0
            for file in self.dos:
                headers=open(file).readlines()[2].split()[2:] # skips the # and ENERGY
                for h in range(len(headers)):
                    self.dos_dict[h+offset] = headers[h]
                offset += len(headers)

        self.energy, self.density_of_states = self.get_dos()

    def get_dos(self):
        density_of_states = []
        for file in self.dos:
            data = np.loadtxt(file, comments='#')
            energy = data[:,0]
            if "dn" in file:
                density_of_states.append(-1*data[:,1:])
            else:
                density_of_states.append(data[:,1:])
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

        for d in range(len(self.density_of_states)):            # loop over the various dos files given
            for s in range(self.density_of_states[d].shape[1]): # loop over the columns in each dos file
                rho = self.density_of_states[d][:,s]
                energy=self.energy
                self.density_of_states[d][:,s][:] = smoother(list(range(len(rho))), energy)

class FermiSurface(object):
    def __init__(self, energy=None, struct=None):

        self.energy = energy
        self.struct = Structure(struct)
        
        if self.energy is None:
            try:
                self.energy = glob.glob("*.energy")[0]
            except:
                raise FileNotFoundError("Could not find a case.energy file in this directory.\nPlease provide a case.energy file")

        def get_fermi_surface(self):
            # from case.energy get kpts and energies
            # interpolate data using griddata
            # return kx, ky grid and surf grid to be plotted
            raise NotImplementedError("This function has not been implemented yet!")

# plotting methods

# plot bandstructure
def band_plot(bands, *opt_list, **opt_dict):
    __band_plot(plt, bands, *opt_list, **opt_dict)

def __band_plot(figure, bands, *opt_list, **opt_dict):
    
    if isinstance(figure, types.ModuleType): figure = figure.gca()
            
    # plot the the dispersion from the bands object
    for b in range(len(bands.Ek)): figure.plot(bands.kpoints, bands.Ek[b,:]-bands.eF_shift, *opt_list, **opt_dict)

    # decorate the figure from here
    figure.set_xticks(bands.high_symmetry_points)
    figure.set_xticklabels(bands.high_symmetry_labels)
    for k in bands.high_symmetry_points: figure.axvline(k, color="k", lw=1)
    figure.axhline(0.0, color="k", lw=1)
    figure.set_ylabel(r"$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)")
    figure.set_ylim(-2, 2); 
    figure.set_xlim(bands.high_symmetry_points[0], bands.high_symmetry_points[-1]);

# band_plot
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
            qtl_file      = open(fat_bands.qtl)
            qtl           = qtl_file.readlines(); qtl_file.close()
            start         = [line+1 for line in range(len(qtl)) if "BAND" in qtl[line]][0]
            qtl           = qtl[start:]
            E         = []
            character = []
            for line in qtl:
                if 'BAND' not in line:
                    if line.split()[1] == str(at):
                        E.append((float(line.split()[0]) - fat_bands.eF)*fat_bands.Ry2eV - fat_bands.eF_shift)    # wien2k interal units are Ry switch to eV
                        enh   = float(fat_bands.weight*fat_bands.structure.atoms[at-1][1])   # weight factor
                        ovlap = (float(line.split()[int(fat_bands.orbitals[a][o]) + 1]))     # qtl overlap
                        character.append(enh*ovlap)
                else:
                    assert len(fat_bands.kpoints) == len(E), "Did not parse file correctly!"
                    assert len(E) == len(character),         "Did not parse file correctly!"
                    figure.scatter(fat_bands.kpoints, E, character, fat_bands.colors[a][o], rasterized=True)
                    E = []
                    character = []

# fatband_plot
mpl.axes.Axes.fatband_plot = lambda self, fat_bands, *opt_list, **opt_dict : __fatband_plot(self, fat_bands, *opt_list, **opt_dict)
                


# plot density of states
def dos_plot(dos, *opt_list, **opt_dict):
    __dos_plot(plt, dos, *opt_list, **opt_dict)


def __dos_plot(figure, dos, *opt_list, **opt_dict):
    if isinstance(figure, types.ModuleType): figure = figure.gca()
    
    offset = 0
    dos_max = 0
    dos_min = 0
    for d in range(len(dos.density_of_states)): # loop over the various dos files given
        for s in range(dos.density_of_states[d].shape[1]): # loop over the columns in each dos file
            if dos_max < np.max(dos.density_of_states[d][:,s]):
                dos_max = np.max(dos.density_of_states[d][:,s])
            if dos_min > np.min(dos.density_of_states[d][:,s]):
                dos_min = np.min(dos.density_of_states[d][:,s])
            figure.plot(dos.energy, dos.density_of_states[d][:,s], label=dos.dos_dict[offset+s], *opt_list, **opt_dict)
        offset += s

    # decorate
    figure.set_xlabel(r'$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)')
    figure.set_ylabel(r'DOS (1/eV)')
    figure.set_xlim(-10, 10)
    if abs(dos_max) > abs(dos_min):
        figure.set_ylim(0, 1.05*dos_max)
    else:
        figure.set_ylim(0.95*dos_min, 1.05*abs(dos_min))
        figure.axhline(0.0, color='k',  lw=1, ls='dotted')
    figure.axvline(0.0, color='k', lw=1, ls='dotted')
    figure.legend(loc="best")

# dos_plot
mpl.axes.Axes.dos_plot = lambda self, dos, *opt_list, **opt_dict : __dos_plot(self, dos, *opt_list, **opt_dict)


# plot fermi surface
#def fermi_surface_plot(fermi_surface):
#    __fermi_surface_plot(plt, fermi_surface)

#def __fermi_surface_plot(figure, fermi_surface):
#    if isinstance(figure, types.ModuleType): figure = figure.gca()

#mpl.axes.Axes.fermi_surface_plot = lambda self, fermi_surface, *opt_list, **opt_dict : __fermi_surface_plot(self, fermi_surface, *opt_list, **opt_dict)

# plot wannier90 bands compared to DFT bands
def wannier_band_plot(wannier_bands, *opt_list, **opt_dict):
    __wannier_band_plot(plt, wannier_bands, *opt_list, **opt_dict)

def __wannier_band_plot(figure, wannier_bands, *opt_list, **opt_dict):
    if isinstance(figure, types.ModuleType): figure = figure.gca()
            
    #plot the wannier bands
    for b in range(len(wannier_bands.wann_bands)):
        figure.plot(wannier_bands.kpts, wannier_bands.wann_bands[b,:], *opt_list, **opt_dict)

    # decorate the figure from here
    figure.axhline(0.0, color="k", lw=1)
    figure.set_ylabel(r"$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)")
    figure.set_ylim(-2, 2); 
    figure.set_xlim(wannier_bands.kpts[0], wannier_bands.kpts[-1])

mpl.axes.Axes.wannier_band_plot = lambda self, wannier_bands, *opt_list, **opt_dict : __wannier_band_plot(self, wannier_bands, *opt_list, **opt_dict)
