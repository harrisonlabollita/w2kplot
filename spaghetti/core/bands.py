#!/usr/bin/python3
import matplotlib.pyplot as plt
import numpy as np
try:
    plt.style.use("band_publish")
except:
    print("Could not find band_publish style. This is available on Github.")

def helpPROCAR(procar):
    f = open(procar, "r")
    lines = f.readlines()
    numKpoints = int(lines[1].split()[3])
    numBands   = int(lines[1].split()[7])
    return numKpoints, numBands

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

