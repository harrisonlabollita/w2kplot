#!/usr/bin/env python
import matplotlib.pyplot as plt
from w2kplot.bands import FatBands, fatband_plot

dft = FatBands(atoms=[2, 4, 3],                 # 2 = V, 3=Sb1, 4=Sb2 (see struct file)
               # 7=d, 3=p, 3=p (see header of qtl file)
               orbitals=[[7], [3], [3]],
               case='cs35',
               colors=[['dodgerblue'], ['forestgreen'], ['tomato']],
               weight=50)

fig, ax = plt.subplots(figsize=(3, 3))
ax.fatband_plot(dft, "k-", lw=1.5)
fig.legend(handles=dft.create_legend(), ncol=3, loc="upper center")
plt.savefig('plot.png', dpi=300)
