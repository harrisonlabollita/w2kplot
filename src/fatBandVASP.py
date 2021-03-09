import matplotlib.pyplot as plt
plt.style.use('band_publish')
import numpy as np


plt.figure(figsize = (6,6))
kpts = []
Ek   = []
#bands = np.zeros((240, 280))
#b = 0
bands = []
for _, line in enumerate(open('band.dat', 'r')):
    try:
        kpts.append(float(line.split()[0]))
        Ek.append(float(line.split()[1])-0.38)
    except:
        plt.plot(kpts, Ek, 'k-', lw = 1)
        bands.append(Ek)
        if len(kpts) > 200:
            kpath = kpts
        kpts = []
        Ek = []

atoms = [1,10, 11]
orbitals = [[8],[8], [4, 6]]
colors = [['#3E2DA5'],['#3E2DA5'], ['#FD9426', '#BA98FC']]
weights = [[25],[25], [200, 200]]
for i in range(len(atoms)):
    for j in range(len(orbitals[i])):
        procar = open('PROCAR', 'r')
        orbital_weight = []
        for _, line in enumerate(procar):
            if len(line) > 10:
                if line.split()[0] == str(atoms[i]):
                    orbital_weight.append(float(line.split()[orbitals[i][j] + 1])*weights[i][j])
        orbital_weight = np.array(orbital_weight).reshape(280, 240)
        for q in range(1, len(bands)-1):
            plt.scatter(kpath, bands[q], s = [row[q -1] for row in orbital_weight], c = colors[i][j], rasterized = True)

kpoints = [0.0000, 0.8139, 1.6278, 2.7788, 2.8597, 3.6736, 4.4875, 5.6385]
klabels = [r'$\Gamma$', 'X', 'M', r'$\Gamma$', 'Z', 'R', 'A', 'Z']
plt.xticks(kpoints, klabels)
for k in kpoints:
    plt.plot([k for i in range(100)], np.linspace(-8, 4, 100), 'k-', lw = 0.5)
plt.xlim(np.min(kpath), np.max(kpath))
plt.plot(np.linspace(0, np.max(kpath), 100), [0 for i in range(100)], 'k-', lw = 0.5)
plt.ylabel('Energy (eV)', fontsize = 20)
plt.ylim(-3, 2.5)
#plt.savefig('Nd6512_NGO_fatBand.pdf', format = 'pdf')
plt.show()
