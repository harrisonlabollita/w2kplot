import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
plt.style.use('band_publish')

class fatBAND():
    def __init__(self, qtlfile, spaghetti, kpath, klabels, Fermi, atoms, orbitals, weight_factor, color):
        self.qtlfile = qtlfile
        self.spaghetti = spaghetti
        self.atoms = atoms
        self.orbitals = orbitals
        self.Fermi = Fermi
        self.kpath = kpath
        self.klabels = klabels
        self.weight_factor = weight_factor
        self.colors = color

    def plot(self):
        plt.figure(figsize = (4, 6))
        spaghetti = open(self.spaghetti, 'r')
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
        for i in range(len(self.atoms)):
            for j in range(len(self.orbitals[i])):
                qtl = open(self.qtlfile, 'r')
                E = []
                orbital_weight = []
                for q, line in enumerate(qtl):
                    if 'BAND' not in line:
                        if line.split()[1] == str(self.atoms[i]):
                            E.append((float(line.split()[0]) - self.Fermi)*13.6)
                            orbital_weight.append(self.weight_factor*(float(line.split()[self.orbitals[i][j] + 1])))
                    else:
                       #plt.plot(kpts, E, 'k-', lw = 1)
                        plt.scatter(kpts, E, orbital_weight, color = self.colors[i][j], edgecolor = 'black', linewidth = 0.5, rasterized = True)
                        E = []
                        orbital_weight = []
        for k in self.kpath:
            plt.plot([k for i in range(100)], np.linspace(-8,4, 100), 'k-', lw = 0.5)
        plt.plot(np.linspace(0, 3, 100), [0 for i in range(100)], 'k-', lw = 1)
        plt.ylim(-4, 4)
        plt.xlim(0, np.max(self.kpath))
        plt.xticks(self.kpath, self.klabels)
        plt.ylabel(r'E$-$E$_{F}$ (eV)', fontsize = 15)
        plt.savefig('5410_d875_fatband.pdf', format = 'pdf', dpi = 150)
        #plt.show()
        #plt.savefig('5410_Ni%s_dn.pdf' %(str(self.atoms[0]-6)), format = 'pdf', dpi = 200)
        #plt.show()

qtlfile = '5410_AFM_U.qtlup'
spaghetti = '5410_AFM_U.spaghettiup_ene'
kpath = [0.00, 0.29610, 0.59221, 1.01097] #1.06134, 1.35745, 1.65355, 2.07231] #5410
klabels = [r'$\Gamma$', 'X', 'M', r'$\Gamma$'] # 'Z', 'R', 'A', 'Z']
Fermi = 0.68242
atom = [7, 8, 9, 10] #Ni1
orbital = [[8], [8], [8], [8]] #dz2, dx2-y2, dxy, dyz, dxz
weight_factor = 100
color = [['blue', 'red'], ['b', 'r'], ['b', 'r'], ['b', 'r']]

fatBAND(qtlfile, spaghetti, kpath, klabels, Fermi, atom, orbital, weight_factor, color).plot()
