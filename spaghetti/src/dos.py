#!/usr/bin/env python
import numpy as np
import sys, glob, os
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from spaghetti.src.w2kstruct import w2kstruct as struct

try:
    plt.style.use("publish")
except:
    print("Spaghetti matplotlib style sheet not found!")


class Error(Exception):
    """base error class."""
    pass


class dos(object):

    def __init__(self):
