#!/usr/bin/env python
import matplotlib.pyplot as plt
from w2kplot import *

dft = FatBands(atoms=[2,4,3],                 # 2 = V, 3=Sb1, 4=Sb2 (see struct file)
              orbitals=[[7],[3],[3]], # 7=d, 3=p, 3=p (see header of qtl file)
              colors=[['dodgerblue'],['forestgreen'],['tomato']],
              weight  = 50)

fig, ax = plt.subplots(figsize=(3,3))
ax.fatband_plot(dft, "k-", lw=1.5)
fig.legend(handles=dft.create_legend(), ncol=3, loc="upper center")
plt.savefig('plot.png', dpi=300)

