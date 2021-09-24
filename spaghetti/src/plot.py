#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import sys
import glob
import os

def band_data(filename):
    data = np.loadtxt(filename, comments="bandindex")
    kpts = np.unique(data[:, 3])
    Ek = data[:,4].reshape(int(len(data)/len(kpts)), len(kpts))
    return kpts, Ek

def arg2latex(string):
    if string == '\\xG':
        return '$\Gamma$'
    else:
        return string

def kpath(filename):
    info = open(filename).readlines()
    kpts = []
    klabel = []
    for (i, line) in enumerate(info):
        if "xaxis" in line and "tick major" in line and "grid" not in line:
            pt = info[i+1].split("\"")[1].strip()
            if pt != "":
                kpts.append(float(line.split(",")[1].strip()))
                klabel.append(arg2latex(pt))
    return kpts, klabel

def fermi(filename):
    scf = open(filename).readlines()
    return float([line for line in scf if ":FER" in line][-1].split()[-1].strip())

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
        extensions = ["*.spaghetti_ene", "*.scf", "*.agr", "*.qtl"]
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
        self.qtl   = glob.glob("*.qtl")[0]
        self.scf   = glob.glob("*.scf")[0]
        self.agr   = glob.glob("*.agr")[0]


    def get_bands(self):
        bands = open(self.bands)
        k = []
        Ek = []
        for i, line in enumerate(bands):
            if 'bandindex' not in line:
                k.append(float(line.split()[3]))
                E.append(float(line.split()[4]))
            else:
                numk = len(k)
        self.kpts = np.array(k).reshape(numk, int(len(k)/numk))
        self.Ek = np.array(Ek).reshape(numk, int(len(Ek)/numk))




try:
    plt.style.use("band_publish")
except:
    print("Could not find band_publish style. This is available on Github.")


def bands(args):
    if args.code == "wien2k":
        plt.figure(figsize = (4, 6))
        spaghetti = open(args.bands, 'r')
        k = []
        E = []
        for i, line in enumerate(spaghetti):
            if 'bandindex' not in line:
                k.append(float(line.split()[3]))
                E.append(float(line.split()[4]))
            else:
                plt.plot(k, E, 'k-', lw = 0.75)
                kpts = k
                k = []
                E = []
        if args.character != None:
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
        tick_labels = args.klabels
        for t in range(len(tick_labels)):
            if tick_labels[t] == "Gamma":
                tick_labels[t] = "$\Gamma$"
        plt.xticks(args.kpath, tick_labels)
        if len(args.kpath) != 0:
            for k in args.kpath:
                plt.plot([k for i in range(100)], np.linspace(args.ymin, args.ymax, 100), 'k-', lw = 0.5)
            plt.plot(np.linspace(np.min(args.kpath), np.max(args.kpath), 100), [0 for i in range(100)], 'k-', lw = 1)
            plt.xlim(0, np.max(args.kpath))
            plt.xticks(args.kpath, args.klabels)
        plt.ylim(args.ymin, args.ymax)
        plt.ylabel(r'Energy (eV)', fontsize = 15)
        if args.save != None:
            plt.savefig(args.save + '.pdf', format = 'pdf', dpi = 150)
        else:
            plt.show()
    elif args.code == "vasp":
        plt.figure(figsize=(6,6))
        kpts = []
        Ek   = []
        bands = []
        for _, line in enumerate(open(args.bands, 'r')):
            try:
                kpts.append(float(line.split()[0]))
                Ek.append(float(line.split()[1]))
            except:
                plt.plot(kpts, Ek, 'k-', lw = 1)
                bands.append(Ek)
                if len(kpts) > 200:
                    kpath = kpts
                    kpts = []
                    Ek = []

        if args.character != None:
            numKpoints, numBands = helpPROCAR(args.character)
            for i in range(len(args.atoms)):
                for j in range(len(args.orbitals[i])):
                    procar = open(args.character, 'r')
                    orbital_weight = []
                    for _, line in enumerate(procar):
                        if len(line) > 10:
                            if line.split()[0] == str(args.atoms[i]):
                                orbital_weight.append(float(line.split()[int(args.orbitals[i][j]) + 1])*float(args.weight_factor[i][j]))
                    orbital_weight = np.array(orbital_weight).reshape(numKpoints, numBands)
                    for q in range(1, len(bands)-1):
                        plt.scatter(kpath, bands[q], s = [row[q -1] for row in orbital_weight], c = args.colors[i][j], rasterized = True)
        tick_labels = args.klabels
        for t in range(len(tick_labels)):
            if tick_labels[t] == "Gamma":
                tick_labels[t] = "$\Gamma$"

        plt.xticks(args.kpath, tick_labels)
        for k in args.kpath:
            plt.plot([k for i in range(100)], np.linspace(np.min(bands), np.max(bands), 100), 'k-', lw = 0.5)
        plt.xlim(np.min(kpath), np.max(kpath))
        plt.plot(np.linspace(0, np.max(kpath), 100), [0 for i in range(100)], 'k-', lw = 0.5)
        plt.ylabel('Energy (eV)', fontsize = 20)
        plt.ylim(args.ymin,args.ymax)
        if args.save != None:
            plt.savefig(args.save + '.pdf', format = 'pdf', dpi = 150)
        else:
            plt.show()

