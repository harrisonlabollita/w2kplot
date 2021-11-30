#!/usr/bin/env python
import numpy as np
import sys, glob, os
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from w2kplot.src.w2kstruct import w2kstruct as struct

class Error(Exception):
    """base error class."""
    pass


class dos(object):

    def __init__(self, args):
        self.args = args

        self.plot_dos()

    def get_int(self):
        try:
            self.int_file = glob.glob("*.int")[0]
        except:
            print("Could not find case.int file in current directory")
        f = open(self.int_file).readlines()
        num_names = int(f[2].split()[0])
        self.dos_names = f[3:3+num_names]
        self.dos_names = [n[[s for s in range(len(n)) if n[s].isalpha()][0]:] for n in self.dos_names]


    def get_dos_data(self):
        try:
            self.dos_file = glob.glob("*.dos1ev")[0]
        except:
            print("[ERROR] Could not find dos file in current path!")
            sys.exit(1)
        self.dos_data = np.loadtxt(self.dos_file, comments="#")


    def plot_dos(self):
        plt.style.use("w2kplot")

        self.get_int()
        self.get_dos_data()
        plt.figure()

        Emesh = self.dos_data[:,0]
        for iname, name in enumerate(self.dos_names):
            if self.args.orientation == "h":
                plt.plot(Emesh, self.dos_data[:,iname+1])
            elif self.args.orientation == "v":
                plt.plot(self.dos_data[:,iname+1], Emesh)

