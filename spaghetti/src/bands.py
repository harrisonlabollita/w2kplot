#!/usr/bin/env python
import numpy as np
import sys, glob, os
from numba import jit
import matplotlib.pyplot as plt
from spaghetti.src.w2kstruct import w2kstruct as struct

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
            self.struct = glob.glob("*.struct")[0]
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

    def arg2latex(self, string):
        if string == '\\xG':
            return '$\Gamma$'
        else:
            return string
    
    def kpath(self):
        # TODO: there is actually a better way to do this
        # Another way to do this would be to get the info from klistband
        # Sometimes this file is incorrect though
        info = open(self.agr).readlines()
        self.high_symm = []
        self.klabel = []
        for (i, line) in enumerate(info):
            if "xaxis" in line and "tick major" in line and "grid" not in line:
                try:
                    pt = info[i+1].split("\"")[1].strip()
                    if pt != "":
                        self.high_symm.append(float(line.split(",")[1].strip()))
                        self.klabel.append(self.arg2latex(pt))
                except:
                    continue

    def fermi(self):
        scf = open(self.scf).readlines()
        self.eF = float([line for line in scf if ":FER" in line][-1].split()[-1].strip())


    def plot_bands(self):
        """program to create band structure plot"""
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
            plt.savefig(self.args.save+".pdf", format="pdf")
        else:
            plt.show()

    def load_init(self): 
        exec(open("spaghetti.init").read())
        load=locals()
        control={}
        control.update(load)
        self.keywords={"klabels": None, 
                   "colors": None, 
                   "atoms" : None, 
                   "orbitals": None,
                   "weights": None}
        for key in self.keywords.keys():
            if key in control.keys():
                self.keywords[key] = control[key]
                

    def plot_fatbands(self):
        ry2eV = 13.6
        default_cols = [[ "dodgerblue" ]]
        # "lightcoral", "dodgerblue", "gold", "forestgreen", "magenta", "mediumslateblue", "cyan", "slategray"
        
        self.band_data()
        self.fermi()
        self.kpath()
        plt.figure()
        for b in range(len(self.Ek)): plt.plot(self.kpts, self.Ek[b,:], "k-", lw=1.5)
        # TODO: is this obsolete?
        if self.qtl is None or self.struct is None or self.scf is None:    # checks for necessary files
            print("Spaghetti needs: case.qtl, case.struct, and case.scf to run fatbands!")
            sys.exit(1)
        if len(glob.glob("spaghetti.init")) == 0:                          # checks for init file
            msg="""To run fatbands, we need a spaghetti.init file.\nTry running spaghetti --init --switch fatbands."""
            print(msg)
            sys.exit(1)

        structure=struct()
        self.load_init()
        self.weight = self.args.weight if self.keywords["weights"] is None else self.keywords["weights"]
        self.colors = default_cols if self.keywords["colors"] is None else self.keywords["colors"]
        for (a, at) in enumerate(self.keywords["atoms"]):
            for o in range(len(self.keywords["orbitals"][a])):
                # opens any qtl file now. No need to delete header
                start=0
                qtl=open(self.qtl).readlines()
                start=[line+1 for line in range(len(qtl)) if "BAND" in qtl[line]][0]
                qtl=qtl[start:]
                E = []
                character = []
                for q, line in enumerate(qtl):
                    if 'BAND' not in line:
                        if line.split()[1] == str(at):
                            E.append((float(line.split()[0]) - self.eF)*ry2eV) # wien2k interal units are Ry switch to eV
                            enh=float(self.weight*structure.atoms[at][1])               # weight factor
                            ovlap=(float(line.split()[int(self.keywords["orbitals"][a][o]) + 1]))       # qtl overlap
                            character.append(enh*ovlap)
                    else:
                        assert len(self.kpts) == len(E), "lenghts of arrays do not match!"
                        assert len(E) == len(character), "lengths of arrays do not match!"
                        plt.scatter(self.kpts, E, character, color=self.colors[a][o], rasterized=True)
                        E = []
                        character = []
        # decorate
        for k in self.high_symm: plt.axvline(k, color="k", lw=0.5)
        plt.axhline(0.0, color="k", lw=0.5)
        plt.ylabel(r"$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)")
        plt.ylim(self.args.ymin, self.args.ymax);
        plt.xlim(np.min(self.high_symm), np.max(self.high_symm));
        if self.keywords["klabels"] is None: 
            plt.xticks(self.high_symm, self.klabel)
        else:
            plt.xticks(self.high_symm, self.keywords["klabels"])
        if self.args.save:
            plt.savefig(self.args.save+".pdf", format="pdf")
        else:
            plt.show()
