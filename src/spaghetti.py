import sys
import matplotlib.pyplot as plt
import numpy as np
try:
    plt.style.use("band_publish")
except:
    print("This mpl-style is not in stylelib. This file is available on GitHub")

from parse import parse
from bands import bands
from dos import dos
from fermi_surface import fermi_surface



def main(args):
    plot(args)
    return

args = parse()
if __name___ == "__main__":
    main(args)
