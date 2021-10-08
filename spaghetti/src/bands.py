#!/usr/bin/env python
import numpy as np
import sys, glob, os
from numba import jit
import matplotlib.pyplot as plt
from struct import *
try:
    plt.style.use("band_publish")
except:
    print("Spaghetti matplotlib style sheet not found")


class bands:
    def __init__(self, args):
        if not self.dir_chk():  # check if the directory contains the files we need
            exit = """Can not find at least a case.spaghetti_ene file!
                      Make sure that you are in the correct directory
                      and that you have at least executed:
                      x lapw1 -band (-p)
                      edit case.insp
                      x spaghetti (-p)

                      For band character plotting, you must run
                      x lapw2 -band -qtl (-p)
                      after lapw1."""
            print(exit)
            sys.exit(1)
        self.args=args
        self.files()            # grab the necessary input files
        if self.args.switch=="bands":
            self.plot_bands()             # plot
        elif self.args.switch=="fatbands":
            self.plot_fatbands()
        else:
            print("Did not recognize that switch ({})".format(args.switch))
            sys.exit(1)


    def dir_chk(self):
        """check if necessary files are in the current working directory!"""
        extensions = ["*.spaghetti_ene","*.agr"]
        for ext in extensions:
            if len(glob.glob(ext)) == 0:
                print("User error: could not find file with extension: {}".format(ext))
                print("Program will not be able to run with this file")
                return False
        return True


    def files(self):
        """load all the necessary files into the spaghetti class."""
        self.bands = glob.glob("*.spaghetti_ene")[0]
        self.agr   = glob.glob("*.agr")[0]
        try:
            self.struct = struct(glob.glob("*.struct")[0])
        except:
            self.struct = None
        try:
            self.qtl   = glob.glob("*.qtl")[0]
        except:
            self.qtl=None
        try:
            self.scf   = glob.glob("*.scf")[0]
        except:
            self.scf = None

    def band_data(self):
        """get the band data from the case.spaghetti_ene"""
        data = np.loadtxt(self.bands, comments="bandindex")
        self.kpts = np.unique(data[:, 3])
        self.Ek = data[:,4].reshape(int(len(data)/len(self.kpts)), len(self.kpts))
        print(self.Ek.shape)

    def arg2latex(self, string):
        if string == '\\xG':
            return '$\Gamma$'
        else:
            return string
    
    def kpath(self):
        # TODO: there is actually a better way to do this
        info = open(self.agr).readlines()
        self.high_symm = []
        self.klabel = []
        for (i, line) in enumerate(info):
            if "xaxis" in line and "tick major" in line and "grid" not in line:
                pt = info[i+1].split("\"")[1].strip()
                if pt != "":
                    self.high_symm.append(float(line.split(",")[1].strip()))
                    self.klabel.append(self.arg2latex(pt))

    @jit
    def fermi(self):
        scf = open(self.scf).readlines()
        self.eF = float([line for line in scf if ":FER" in line][-1].split()[-1].strip())

    @jit
    def fatband(self):
        ry2eV = 13.6
        self.character=[]
        for i in range(len(args.atoms)):
            for j in range(len(args.orbitals[i])):
                # opens any qtl file now. No need to delete header
                start=0
                qtl=open(filename).readlines()
                start=[line+1 for line in range(len(qtl)) if "BAND" in qtl[line]][0]
                qtl=qtl[start:]
                E = []
                orbital_weight = []
                for q, line in enumerate(qtl):
                    if 'BAND' not in line:
                        if line.split()[1] == str(args.atoms[i]):
                            E.append((float(line.split()[0]) - args.fermi)*ry2eV) # wien2k interal units are Ry switch to eV
                            orbital_weight.append(float(args.weight_factor[i][j])*(float(line.split()[int(args.orbitals[i][j]) + 1])))
                    else:
                        self.character.append(orbital_weight)
                        orbital_weight = []
    def plot_bands(self):
        """main program to create band structure plot"""
        self.band_data()
        self.kpath()
        plt.figure()
        for b in range(len(self.Ek)):
            plt.plot(self.kpts, self.Ek[b,:], "k-", lw=1.5)
        plt.xticks(self.high_symm, self.klabel)
        for k in self.high_symm: plt.axvline(k, color="k", lw=0.5)
        plt.axhline(0.0, color="k", lw=0.5)
        plt.ylabel(r"$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)")
        plt.ylim(self.args.ymin, self.args.ymax);
        plt.xlim(np.min(self.high_symm), np.max(self.high_symm));

        if self.args.save:
            plt.savefig("spaghetti_bands.pdf", format="pdf")
        else:
            plt.show()

    def plot_fatbands(self):
        print("Not implemented yet!")
        sys.exit(1)

