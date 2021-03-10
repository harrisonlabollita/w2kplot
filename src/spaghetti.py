import sys

try:
    import matplotlib.pyplot as plt
except:
    print("Need to install matplotlib")

try:
    import numpy as np
except:
    print("Need to install numpy")


class spaghetti:

    class wien2k:
        def plotBands(self, **p):
            plt.figure(figsize = (4, 6))
            spaghetti = open(p["spaghetti"], 'r')
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
            if p["qtlfile"] != None:
                for i in range(len(p["atoms"])):
                    for j in range(len(p["orbitals"][i])):
                        qtl = open(p["qtlfile"], 'r')
                        E = []
                        orbital_weight = []
                        for q, line in enumerate(qtl):
                            if 'BAND' not in line:
                                if line.split()[1] == str(p["atoms"][i]):
                                    E.append((float(line.split()[0]) - p["Fermi"])*13.6)
                                    orbital_weight.append(p["weight_factor"]*(float(line.split()[p["orbitals"][i][j] + 1])))
                            else:
                                plt.scatter(kpts, E, orbital_weight, color = p["colors"][i][j], edgecolor = 'black', linewidth = 0.5, rasterized = True)
                                E = []
                                orbital_weight = []

            for k in p["kpath"]:
                plt.plot([k for i in range(100)], np.linspace(p["ymin"], p["ymax"], 100), 'k-', lw = 0.5)
            plt.plot(np.linspace(np.min(p["kpath"]), np.max(p["kpath"]), 100), [0 for i in range(100)], 'k-', lw = 1)
            plt.ylim(p["ymin"], p["ymax"])
            plt.xlim(0, np.max(p["kpath"]))
            plt.xticks(p["kpath"], p["klabels"])
            plt.ylabel(r'Energy (eV)', fontsize = 15)
            if p["save"] != None:
                plt.savefig(p["save"] + '.pdf', format = 'pdf', dpi = 150)
            else:
                plt.show()

        def plotDOS(self, **p):

            """ plot the density of states given dos files from wien2k
            """

            if p["save"] != None:
                plt.savefig(p["save"] + '.pdf', format = 'pdf')
            else:
                plt.show()


    class vasp:


        def plotBands(self, **p):
            plt.figure(figsize=(6,6))
            kpts = []
            Ek   = []
            bands = []
            for _, line in enumerate(open(p["bands"], 'r')):
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

            if p["procar"] != None:
                for i in range(len(p["atoms"])):
                    for j in range(len(p["orbitals"][i])):
                        procar = open(p["procar"], 'r')
                        orbital_weight = []
                        for _, line in enumerate(procar):
                            if len(line) > 10:
                                if line.split()[0] == str(p["atoms"][i]):
                                    orbital_weight.append(float(line.split()[p["orbitals"][i][j] + 1])*p["weight_facttor"][i][j])
                        orbital_weight = np.array(orbital_weight).reshape(280, 240) # Need to fix this
                        for q in range(1, len(bands)-1):
                            plt.scatter(kpath, bands[q], s = [row[q -1] for row in orbital_weight], c = p["colors"][i][j], rasterized = True)


            plt.xticks(p["kpoints"], p["klabels"])
            for k in p["kpoints"]:
                plt.plot([k for i in range(100)], np.linspace(np.min(bands), np.max(bands), 100), 'k-', lw = 0.5)
            plt.xlim(np.min(kpath), np.max(kpath))
            plt.plot(np.linspace(0, np.max(kpath), 100), [0 for i in range(100)], 'k-', lw = 0.5)
            plt.ylabel('Energy (eV)', fontsize = 20)
            plt.ylim(p["ymin"], p["ymax"])
            if p["save"] != None:
                plt.savefig(p["save"] + '.pdf', format = 'pdf', dpi = 150)
            else:
                plt.show()
