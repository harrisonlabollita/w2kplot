#!/usr/bin/env python

import matplotlib.pyplot as plt
from w2kplot.bands import Bands, band_plot


fig, ax = plt.subplots(1, 2, sharey=True, figsize=(6, 3))

up_channel = Bands.Up()
dn_channel = Bands.Down()
ax[0].band_plot(up_channel, "b-", lw=1)
ax[0].set_title('majority')
ax[1].band_plot(dn_channel, "r-", lw=1)
ax[1].set_title('minority')

plt.subplots_adjust(hspace=0.05)
plt.savefig('plot.png', dpi=300)
plt.show()
