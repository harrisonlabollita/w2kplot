import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
plt.style.use("publish")


def spaghetti():
    fig, ax = plt.subplots(figsize=(3.5,2.5))

    # bands
    x = np.linspace(-0.5*np.pi, 0.5*np.pi, 100)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.plot(x, 0.5*(-np.cos(2*x)+1), '-', color="mediumblue", lw=3)
    ax.plot(x, -0.5*(-np.cos(2*x)-3.5), '-', color="orange", lw=3)
    ax.set_yticks([]); ax.set_xticks([]);
    ax.set_xlabel(r"$k$", loc="right"); ax.set_ylabel(r"$\varepsilon(k)$", loc="top", rotation="45");
    ax.set_xlim(-0.5*np.pi, 0.5*np.pi); ax.set_ylim(0, 2.4);

    # spaghetti logo
    left, width = .25, .5
    bottom, height = .25, .5
    right = left + width
    top = bottom + height
    p = patches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax.transAxes, clip_on=False
    )
    font = {}
    font["size"] = 30
    font["family"] = "Helvetica"
    font["weight"] = "bold"
    

    sym = ax.text(0.5*(left+right), 0.5*(bottom+top), 'spaghetti',
        horizontalalignment='center',
        verticalalignment='center',
        transform=ax.transAxes, fontdict=font)
    font = {}
    font["size"] = 10
    font["color"] = "dimgrey"
    font["family"] = "Helvetica"
    sub = ax.text(0.5*(left+right), 0.35*(bottom+top), 'command-line plotting tool',
        horizontalalignment='center',
        verticalalignment='center',
        transform=ax.transAxes, fontdict=font)
    plt.savefig("logo.png", transparent=True, dpi=300)

if __name__ == "__main__":
    spaghetti()

