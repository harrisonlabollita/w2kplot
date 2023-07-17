# -*- coding: utf-8 -*-

##########################################################################
#
# w2kplot: a thin Python wrapper around matplotlib
#
# Copyright (C) 2022 Harrison LaBollita
# Authors: H. LaBollita
#
# w2kplot is free software licensed under the terms of the MIT license.
#
##########################################################################

import glob
import types
from typing import Union, List, Dict


class Structure(object):
    """this is a wien2k structure class that contains the information
       we need about about the crystal structure to plot the bands.
    """

    def __init__(self, filename: str) -> None:
        """
        Initialize the structure class. This is used to contain information
        about the crystal structure store in filename.
        This class is intended to only be used internally by w2kplot.

        Parameters
        ----------
        filename : string, optional
                   Filename of case.struct. If not given glob.glob will search current directory
                   for file with extension .struct.
        """
        if filename is None:
            try: self._load()
            except BaseException: raise FileNotFoundError("Couldn't find a case.struct file in this directory!")
        else:
            self._load(filename=filename)

    def _load(self, filename: str = None) -> None:
        """
        Function to parse struct file and store the data into the Structure class

        Parameters
        ----------
        filename : string, optional
                   Filename of case.struct. If not given glob.glob will search current directory
                   for file with extension .struct.
        """
        if filename is None:
            struct_file = open(glob.glob("*.struct")[0])
            contents = struct_file.readlines()
            struct_file.close()
        else:
            f = open(filename)
            contents = f.readlines()
            f.close()

        try:  # does this try/except handle all cases
            self.nat = int(contents[1].split()[2])
            self.spg = int(contents[1].split()[3])
        except BaseException:
            self.nat = int(contents[1].split()[1])
            self.spg = int(contents[1].split()[2])

        iatom = list(range(1, self.nat + 1))
        mults = [int(line.split("=")[1].split()[0])
                 for line in contents if "MULT" in line]
        specs = [str(line.split()[0]) for line in contents if "NPT" in line]

        self.atoms = {}
        assert len(mults) == len(
            specs), "The struct file was not parsed correctly!"
        assert len(iatom) == len(
            specs), "The struct file was not parsed correctly!"
        for a in range(self.nat):
            self.atoms[a] = [specs[a], mults[a]]

        # TODO: load symmetries?
        # load the symmetries in the structure here as well.
        # store them in self.symmetries

    # dunder functions
    def __getitem__(self, key): return self.atoms[key]

