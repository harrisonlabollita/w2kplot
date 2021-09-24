#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import sys
import glob
import os



class spaghetti:
    def __init__(self):
        if not self.directory_checkup():
            exit = """Can not find at least a case.spaghetti_ene file!
                      Make sure that you are in the correct directory
                      and that you have at least executed:
                      x lapw1 -band (-p)
                      edited case.insp
                      x spaghetti (-p)

                      For band character plotting, you must run
                      x lapw2 -band -qtl (-p)
                      after lapw1."""
            print(exit)
            sys.exit(1)
        # TODO- check for style sheet
        self.get_files()
        self.get_command_line()


    def directory_checkup(self):
        """check if necessary files are in the current working directory"""
        extensions = ["*.spaghetti_ene", "*.scf", "*.agr", "*.qtl", "*.struct"]
        for ext in extensions:
            if len(glob.glob(ext)) == 0:
                print("User error: could not find file with extension: {}".format(ext))
                return False
        return True

    def get_command_line(self):
        parser.add_argument("--atoms", nargs="+", type = int, default=[], help = "if plotting band character indcies of atoms to plot the character for")
        parser.add_argument("--orbitals", nargs="+", default=[], help = "indices of orbitals to plot band character for")
        parser.add_argument("--fermi", type = float, default = None, help = "Fermi energy")
        parser.add_argument("--ymin", type = float, default = -1.5)
        parser.add_argument("--xmin", type = float, default = None)
        parser.add_argument("--xmax", type = float, default = None)
        parser.add_argument("--ymax", type = float, default = 1.5)
        parser.add_argument("--kpath", nargs="+", default = [], help = "points along the highsymmetry points")
        parser.add_argument("--klabels", nargs="+", default = [], help = "High symmetry points labels")
        parser.add_argument("--colors", nargs = "+", default = [], help = "colors to plot")
        parser.add_argument("--weight_factor", nargs="+", default = [], help = "weights multiply character by")
        parser.add_argument("--save", default = None, help = "option to save the image")
        args = parser.parse_args()
        args.kpath = list(map(float, args.kpath))
        args.colors = adjustArray(args.colors)
        args.orbitals = adjustArray(args.orbitals)
        args.weight_factor  = adjustArray(args.weight_factor)

    def get_files(self):
        self.bands = glob.glob("*.spaghetti_ene")[0]
        self.struct = glob.glob("*.struct")[0]
        self.qtl   = glob.glob("*.qtl")[0]
        self.scf   = glob.glob("*.scf")[0]
        self.agr   = glob.glob("*.agr")[0]


    def band_data(self):
        data = np.loadtxt(self.bands, comments="bandindex")
        self.kpts = np.unique(data[:, 3])
        self.Ek = data[:,4].reshape(int(len(data)/len(kpts)), len(kpts))


    def arg2latex(self, string):
        if string == '\\xG':
            return '$\Gamma$'
        else:
            return string

    def kpath(self):
        info = open(self.agr).readlines()
        self.kpts = []
        self.klabel = []
        for (i, line) in enumerate(info):
            if "xaxis" in line and "tick major" in line and "grid" not in line:
                pt = info[i+1].split("\"")[1].strip()
                if pt != "":
                    self.kpts.append(float(line.split(",")[1].strip()))
                    self.klabel.append(self.arg2latex(pt))

    def fermi(self):
        scf = open(self.scf).readlines()
        self.eF = float([line for line in scf if ":FER" in line][-1].split()[-1].strip())

    def fatband(self)
        for i in range(len(args.atoms)):
            for j in range(len(args.orbitals[i])):
                qtl = open(args.character, 'r')
                E = []
                orbital_weight = []
                for q, line in enumerate(qtl):
                    if 'BAND' not in line:
                        if line.split()[1] == str(args.atoms[i]):
                            E.append((float(line.split()[0]) - args.fermi)*13.6) # wien2k interal units are Ry switch to eV
                            orbital_weight.append(float(args.weight_factor[i][j])*(float(line.split()[int(args.orbitals[i][j]) + 1])))
                    else:
                        plt.scatter(kpts, E, orbital_weight, color = args.colors[i][j], edgecolor = 'black', linewidth = 0.5, rasterized = True)
                        E = []
                        orbital_weight = []

    def plot(self):
        """create band structure plot."""

