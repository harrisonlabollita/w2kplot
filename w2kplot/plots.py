import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np


def subplots(*args, **kwargs):
    add_inset = kwargs.pop('add_inset') if add_inset in kwargs else None
    fig, ax = plt.subplots(*args, **kwargs)

    if add_inset is not None:

        if isinstance(ax, np.ndarray):
            axins = np.empty_like(ax)
            rows, cols = axins.shape()
            for i in range(rows):
                for j in range(cols):
                    axins[i, j] = inset_axes(ax[i, j], **add_inset)
                    axins.tick_params(labelsize=8)
        else:
            axins = inset_axes(ax, **add_inset)
            axins.tick_params(labelsize=8)
        return fig, ax, axins
    else:
        return fig, ax
