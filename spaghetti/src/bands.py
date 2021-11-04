#!/usr/bin/env python
import numpy as np
import sys, glob, os
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from spaghetti.src.w2kstruct import w2kstruct as struct

try:
    plt.style.use("band_publish")
except:
    print("Spaghetti matplotlib style sheet not found!")


class Error(Exception):
    """base error class."""
    pass

class KlistBandError(Exception):
    """Raised when there is an error parsing the the *.klist_band file."""
    pass

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
            if self.args.spin is not None:
                print("Plotting fatbands for spin-polarized calculations is not supported yet!")
                sys.exit(1)
            self.plot_fatbands()
        else:
            print("Did not recognize that switch ({})".format(args.switch))
            sys.exit(1)


    def dir_chk(self):
        """check if necessary files are in the current working directory!"""
        extensions = ["*.spaghetti*","*.klist_band"]
        for ext in extensions:
            if len(glob.glob(ext)) == 0:
                print("User error: could not find file with extension: {}".format(ext))
                print("Program will not be able to run with this file")
                return False
        return True

    def files(self):
        """load all the necessary files into the spaghetti class."""
        if self.args.spin is not None:
            self.bands = [glob.glob("*.spaghettiup_ene")[0], glob.glob("*.spaghettidn_ene")[0]]
        else:
            self.bands = glob.glob("*.spaghetti_ene")[0]
        
        self.klist   = glob.glob("*.klist_band")[0]
        try:
            self.struct = glob.glob("*.struct")[0]
        except:
            self.struct = None
        try:
            if self.args.spin is not None:
                self.qtl   = [glob.glob("*.qtlup")[0], glob.glob("*.qtldn")[0]]
            else:
                self.qtl = glob.glob("*qtl")[0]
        except:
            self.qtl =None
        try:
            self.scf   = glob.glob("*.scf")[0]
        except:
            self.scf = None
        

    def band_data(self):
        """get the band data from the case.spaghetti_ene"""
        if self.args.spin is not None:
            data_up = np.loadtxt(self.bands[0], comments="bandindex")
            self.kpts = np.unique(data_up[:, 3])
            data_dn = np.loadtxt(self.bands[1], comments="bandindex")
            self.Ek = [data_up[:,4].reshape(int(len(data_up)/len(self.kpts)), len(self.kpts)),
                       data_dn[:,4].reshape(int(len(data_dn)/len(self.kpts)), len(self.kpts))]
        else:
            data = np.loadtxt(self.bands, comments="bandindex")
            self.kpts = np.unique(data[:, 3])
            self.Ek = data[:,4].reshape(int(len(data)/len(self.kpts)), len(self.kpts))

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
    
    def kpath(self):
        """get the high symmetry points and labels from klist band."""
        klist = open(self.klist).readlines()
        self.high_symm = []
        self.klabel = []
        try:
            for il, line in enumerate(klist):
                if line[:3] == "END": break
                if line[:10].split():
                    self.klabel.append(self.arg2latex(line.strip().split()[0]))
                    self.high_symm.append(il)
            self.high_symm = [self.kpts[ind] for ind in self.high_symm]
        except KlistBandError:
            print("spaghetti encountered an error when parsing the {} file".format(self.klist))
            print("You can define custom labels and high-symmetry points\n in the spaghetti.init file")

    def fermi(self):
        """get the Fermi energy (eF) from the case.scf file."""
        self.eF = float([line for line in open(self.scf).readlines() if ":FER" in line][-1].split()[-1].strip())

    def plot_bands(self):
        """program to create band structure plot"""
        self.band_data()
        self.kpath()
        if self.args.spin  == "join":
            fig, ax = plt.subplots()
            for b in range(len(self.Ek[0])): ax.plot(self.kpts, self.Ek[0][b,:], "b-", lw=1.5)
            for b in range(len(self.Ek[1])): ax.plot(self.kpts, self.Ek[1][b,:], "r.-", lw=1.5)

        elif self.args.spin == "sep":
            fig, ax = plt.subplots(1, 2, sharey=True)
            for b in range(len(self.Ek[0])): ax[0].plot(self.kpts, self.Ek[0][b,:], "b-", lw=1.5)
            for b in range(len(self.Ek[1])): ax[1].plot(self.kpts, self.Ek[1][b,:], "r.-", lw=1.5)
        else:
            fig, ax = plt.subplots()
            for b in range(len(self.Ek)): plt.plot(self.kpts, self.Ek[b,:], "k-", lw=1.5)

        if self.args.spin == "sep":
            for p in range(2): 
                ax[p].set_xticks(self.high_symm)
                ax[p].set_xticklabels(self.klabel)
                for k in self.high_symm: ax[p].axvline(k, color="k", lw=0.5)
                ax[p].axhline(0.0, color="k", lw=0.5)
                ax[0].set_ylabel(r"$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)")
                ax[0].set_ylim(self.args.ymin, self.args.ymax); 
                ax[p].set_xlim(np.min(self.high_symm), np.max(self.high_symm));
        else:
            ax.set_xticks(self.high_symm,)
            ax.set_xticklabels(self.klabel)
            for k in self.high_symm: ax.axvline(k, color="k", lw=0.5)
            ax.axhline(0.0, color="k", lw=0.5)
            ax.set_ylabel(r"$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)")
            ax.set_ylim(self.args.ymin, self.args.ymax); 
            ax.set_xlim(np.min(self.high_symm), np.max(self.high_symm));

        if self.args.spin is not None: 
            legend_elements = [Line2D([0], [0], linestyle= '-',color="b", lw=3, label="up"),
                               Line2D([0], [0], linestyle="-", color="r", lw=3, label="down")]
            fig.legend(handles=legend_elements, loc="upper left")

        if self.args.save:
            plt.savefig(self.args.save+".pdf", format="pdf", dpi=300)
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
                       "weight": None}
        for key in self.keywords.keys():
            if key in control.keys():
                self.keywords[key] = control[key]
    
    def get_orb_labels(self, atom, orbs):
        """grabs the labels of the fatbands plotted from the qtl file and returns an array labels."""
        qtl2orb = {    "PZ"        : r"$p_{z}$",
                       "PX"        : r"$p_{x}$",
                       "PY"        : r"$p_{y}$",
                       "PX+PY"     : r"$p_{x}+p_{y}$",
                       "DZ2"       : r"$d_{z^{2}}$",
                       "DX2Y2"     : r"$d_{x^{2}+y^{2}}$",
                       "DXZ"       : r"$d_{xz}$",
                       "DYZ"       : r"$d_{yz}$",
                       "DXY"       : r"$d_{xy}$",
                       "DX2Y2+DXY" : r"$d_{x^{2}+y^{2}}+d_{xy}$",
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
    
    def create_legend(self, structure):
        legend_elements = []
        for (ia, a) in enumerate(self.keywords["atoms"]):
            labels=self.get_orb_labels(a, self.keywords["orbitals"][ia])
            for o in range(len(self.keywords["orbitals"][ia])):
                legend_elements.append(Line2D([0], [0], 
                                       linestyle= '-', 
                                       color=self.colors[ia][o], 
                                       lw=3, 
                                       label=structure.atoms[a-1][0]+"-"+labels[o]))
        return legend_elements

    def plot_fatbands(self):
        ry2eV = 13.6

        default_cols = [["dodgerblue", "lightcoral", "gold", "forestgreen", "magenta"],
                        ["b", "r", "g", "y", "c"],
                        ["royalblue", "salmon", "lawngreen", "orange", "deeppink"]]
        self.band_data()       # get the bands
        self.fermi()           # get εF
        self.kpath()           # get the kpath
        fig, ax = plt.subplots()

        for b in range(len(self.Ek)): ax.plot(self.kpts, self.Ek[b,:], "k-", lw=1.5)
        # perform some checks to make sure we have necessary files  
        if self.qtl is None or self.struct is None or self.scf is None:    # checks for necessary files
            print("Spaghetti needs: case.qtl, case.struct, and case.scf to run fatbands!")
            sys.exit(1)
        if len(glob.glob("spaghetti.init")) == 0:                          # checks for init file
            msg="""To run fatbands, we need a spaghetti.init file.\nTry running spaghetti --init --switch fatbands."""
            print(msg)
            sys.exit(1)

        structure=struct() # initialize a struct object
        
        self.load_init() # load info from the spaghetti.init file
        
        self.weight = self.args.weight if self.keywords["weight"] is None else self.keywords["weight"]
        
        if self.keywords["colors"] is None:
            self.colors = [[default_cols[ia%len(default_cols)][o%len(default_cols[0])]  \
                           for o in self.keywords["orbitals"][ia]]  \
                           for (ia, a) in enumerate(self.keywords["atoms"])]
        else:
            self.colors = self.keywords["colors"]
       
        for (a, at) in enumerate(self.keywords["atoms"]):
            for o in range(len(self.keywords["orbitals"][a])):
                qtl           = open(self.qtl).readlines() 
                start         = [line+1 for line in range(len(qtl)) if "BAND" in qtl[line]][0]
                qtl           = qtl[start:]
                E         = []
                character = []
                
                for line in qtl:
                    if 'BAND' not in line:
                        if line.split()[1] == str(at):
                            E.append((float(line.split()[0]) - self.eF)*ry2eV)                      # wien2k interal units are Ry switch to eV
                            enh   = float(self.weight*structure.atoms[at-1][1])                       # weight factor
                            ovlap = (float(line.split()[int(self.keywords["orbitals"][a][o]) + 1])) # qtl overlap
                            character.append(enh*ovlap)
                    else:
                        assert len(self.kpts) == len(E), "lenghts of arrays do not match!"
                        assert len(E) == len(character), "lengths of arrays do not match!"
                        ax.scatter(self.kpts, E, character, color=self.colors[a][o], rasterized=True)
                        E = []
                        character = []
        # decorate
        for k in self.high_symm: ax.axvline(k, color="k", lw=0.5)
        ax.axhline(0.0, color="k", lw=0.5)
        ax.set_ylabel(r"$\varepsilon - \varepsilon_{\mathrm{F}}$ (eV)")
        ax.set_ylim(self.args.ymin, self.args.ymax);
        ax.set_xlim(np.min(self.high_symm), np.max(self.high_symm));

        # create the legend
        if self.args.legend == "center":
            legend_handles=self.create_legend(structure)
            fig.legend(handles=legend_handles, loc="upper center", ncol=len(legend_handles), fontsize = 10)
        elif self.args.legend == "right":
            legend_handles=self.create_legend(structure)
            fig.legend(handles=legend_handles, loc="upper right", fontsize = 10)
        elif self.args.legend == "left":
            legend_handles=self.create_legend(structure)
            fig.legend(handles=legend_handles, loc="upper left", fontsize = 10)

        if self.keywords["klabels"] is None: 
            ax.set_xticks(self.high_symm)
            ax.set_xticklabels(self.klabel)
        else:
            assert len(self.high_symm) == len(self.keywords["klabels"]), "number of k labels provided does not match number of high-symmetry points!"
            ax.set_xticks(self.high_symm)
            ax.set_xticklabels(self.keywords["klabels"])

        if self.args.save:
            plt.savefig(self.args.save+".png", format="png", dpi=300)
        else:
            plt.show()
