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

from fractions import Fraction
from math import gcd
from typing import Dict, List, Tuple

import numpy as np

# WIEN2k writes k-points in case.klist as integer triples (ix, iy, iz) over a
# common divisor, expressed in the *conventional* reciprocal lattice basis.
# The high symmetry points we get from ase are in the *primitive* reciprocal
# basis, so they have to be transformed (see KPath._to_conventional).

# smallest divisor used for segments whose endpoints are not simple fractions
_RESOLUTION = 10000

# the klist_band format gives every integer 5 columns, so the numerators and
# the divisor have to stay within 5 characters, sign included
_MAX_FIELD = 9999

_MISSING_DEPS = (
    "w2kplot-kgen needs ase and spglib to detect the symmetry of the struct "
    "file and to look up the high symmetry points:\n\n    pip install ase spglib\n"
)


def _require_deps():
    try:
        import spglib  # noqa: F401
        from ase.io.wien2k import c2p, coorsys, read_struct
    except ImportError:
        raise ImportError(_MISSING_DEPS)
    return read_struct, coorsys, c2p


def _lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)


def _denominator(x: float, max_den: int = 24, tol: float = 1e-6) -> int:
    """
    Denominator of x if x is a simple fraction, else 0.

    Most high symmetry points are simple fractions (1/2, 1/3, 3/8, ...) and we
    want those to come out exact. Some Bravais lattices (BCT, RHL, ORCF, MCL)
    have points that depend continuously on the lattice parameters; those are
    not fractions at all and have to be rounded onto the k-mesh instead.
    """
    frac = Fraction(x).limit_denominator(max_den)
    return frac.denominator if abs(float(frac) - x) < tol else 0


def _as_fraction_str(x: float, max_den: int = 24, tol: float = 1e-6) -> str:
    """Pretty print a high symmetry point coordinate."""
    frac = Fraction(x).limit_denominator(max_den)
    if abs(float(frac) - x) > tol:
        return "{:.5f}".format(x)
    return str(frac.numerator) if frac.denominator == 1 else "{}/{}".format(
        frac.numerator, frac.denominator)


class KPath(object):
    """this class detects the symmetry of a wien2k struct file and provides the
       high symmetry points of the corresponding Brillouin zone, in the
       convention wien2k expects in case.klist_band.
    """

    def __init__(self, filename: str, symprec: float = 1e-5) -> None:
        """
        Initialize the KPath class.

        Parameters
        ----------
        filename : string, required
                   Filename of case.struct.
        symprec  : float, optional
                   Symmetry tolerance handed to spglib when determining the
                   space group.
        """
        read_struct, coorsys, c2p = _require_deps()

        cellpar, lattice, positions, species, _ = read_struct(
            filename, ase=False)

        self.filename = filename
        self.lattice = lattice
        self.species = species

        # rows of conventional / primitive are the lattice vectors. wien2k
        # gives the positions in the conventional cell, so they have to be
        # transformed along with the cell.
        self.conventional = coorsys(cellpar)
        self.c2p = np.asarray(c2p(lattice))
        self.primitive = self.c2p @ self.conventional
        self.positions = np.asarray(positions) @ np.linalg.inv(self.c2p)

        self.spacegroup = self._get_spacegroup(symprec)
        self.bravais, self.points, self.recommended = self._get_high_symmetry_points()

    def _get_spacegroup(self, symprec: float) -> str:
        """
        Internal function to determine the space group of the structure with spglib.
        """
        import spglib
        from ase.data import atomic_numbers

        numbers = [atomic_numbers[s.capitalize()] for s in self.species]
        cell = (self.primitive, self.positions, numbers)
        return spglib.get_spacegroup(cell, symprec=symprec)

    def _to_conventional(self, kpoint: np.ndarray) -> np.ndarray:
        """
        Internal function to convert a k-point given in the primitive reciprocal
        basis to the conventional reciprocal basis used by wien2k.

        With the real space cells related by A_prim = M A_conv, equating the
        cartesian k-vector k_prim B_prim = k_conv B_conv and using B = A^-T
        gives k_conv = k_prim M^-T.
        """
        return np.asarray(kpoint) @ np.linalg.inv(self.c2p).T

    def _get_high_symmetry_points(self) -> Tuple[str, Dict[str, np.ndarray], str]:
        """
        Internal function to look up the high symmetry points and the
        recommended path of the Brillouin zone belonging to this structure.
        """
        from ase.cell import Cell
        from ase.dft.kpoints import parse_path_string

        cell = Cell(self.primitive)
        bandpath = cell.bandpath(npoints=0)
        points = {self._rename(label): self._to_conventional(kpoint)
                  for label, kpoint in bandpath.special_points.items()}
        # ase stores the path as a flat string, the labels of which may carry a
        # digit (Z1, S1, ...), so it has to be tokenized rather than iterated.
        recommended = ["-".join(self._rename(label) for label in branch)
                       for branch in parse_path_string(bandpath.path)]
        return str(cell.get_bravais_lattice()), points, ",".join(recommended)

    @staticmethod
    def _rename(label: str) -> str:
        """
        Internal function to convert an ase high symmetry label to the label
        wien2k and w2kplot expect (see Bands._arg2latex).
        """
        return "GAMMA" if label == "G" else label[:10]

    def cartesian(self, kpoint: np.ndarray) -> np.ndarray:
        """
        Convert a k-point in conventional reciprocal coordinates to cartesian
        units of 1/Angstrom. Only the relative lengths matter here, they are
        used to distribute the k-points evenly along the path.

        Parameters
        ----------
        kpoint : np.ndarray, required
                 k-point in conventional reciprocal coordinates.
        """
        return np.asarray(kpoint) @ (2 * np.pi *
                                     np.linalg.inv(self.conventional).T)

    def parse_path(self, path: str) -> List[List[str]]:
        """
        Parse a path of high symmetry labels into branches.

        Labels are separated by whitespace or '-', branches (discontinuous
        jumps in the path) by ',' or '|'.

        Parameters
        ----------
        path : string, required
               e.g. "GAMMA-M-K-GAMMA-A,L-M"
        """
        branches = []
        for branch in path.replace("|", ",").split(","):
            labels = branch.replace("-", " ").split()
            unknown = [label for label in labels if label not in self.points]
            if unknown:
                raise ValueError(
                    "unknown high symmetry point(s) {}, expected one of {}".format(
                        ", ".join(unknown), ", ".join(sorted(self.points))))
            if len(labels) < 2:
                raise ValueError(
                    "a branch of the path needs at least two high symmetry points")
            branches.append(labels)
        if not branches:
            raise ValueError("empty path")
        return branches

    # dunder functions
    def __getitem__(self, key): return self.points[key]
    def __len__(self): return len(self.points)
    def __iter__(self): return self.points.__iter__()


def klist_band(kpath: KPath,
               branches: List[List[str]],
               npoints: int = 300) -> List[Tuple[str, np.ndarray, int]]:
    """
    Generate the k-points of a band structure path.

    The npoints k-points are distributed over the segments of the path
    proportionally to their length in cartesian reciprocal space, so that the
    k-axis of the band plot comes out with the right aspect ratio. Each segment
    gets its own divisor, which keeps the high symmetry points exact wherever
    they are simple fractions.

    Parameters
    ----------
    kpath    : KPath, required
               The KPath object holding the high symmetry points.
    branches : list of list of string, required
               The path, as returned by KPath.parse_path.
    npoints  : integer, optional
               Approximate total number of k-points along the path.

    Returns
    -------
    list of (label, (ix, iy, iz), divisor), where label is empty for the
    k-points in between the high symmetry points.
    """
    segments = [(branch[i], branch[i + 1])
                for branch in branches for i in range(len(branch) - 1)]

    lengths = np.array([np.linalg.norm(kpath.cartesian(kpath[kf] - kpath[ki]))
                        for ki, kf in segments])
    if np.any(lengths == 0):
        raise ValueError("the path contains a segment of zero length")

    # at least one division per segment, and npoints in total
    divisions = np.maximum(1, np.rint(
        (npoints - 1) * lengths / lengths.sum()).astype(int))

    kpoints, iseg = [], 0
    for branch in branches:
        for i in range(len(branch) - 1):
            start, end = branch[i], branch[i + 1]
            ki, kf = kpath[start], kpath[end]
            ndiv = divisions[iseg]
            iseg += 1

            den, exact = 1, True
            for x in np.concatenate([ki, kf]):
                denominator = _denominator(x)
                if denominator:
                    den = _lcm(den, denominator)
                else:
                    exact = False
            divisor = den * ndiv
            # a segment whose endpoints are all simple fractions is already
            # written exactly, the others are refined so that rounding them
            # onto the mesh moves them by less than 1/(2*_RESOLUTION). The
            # refinement is capped so that the numerators, which go up to
            # kmax*divisor, still fit their 5 columns.
            if not exact:
                kmax = max(1.0, float(np.abs(np.concatenate([ki, kf])).max()))
                divisor *= max(1, min(-(-_RESOLUTION // divisor),
                                      int(_MAX_FIELD / kmax) // divisor))

            # the endpoint of the previous segment of this branch is the start
            # of this one, so it is only written once. Where the path jumps to
            # a new branch both endpoints are written, they are different
            # k-points.
            for j in range(0 if i == 0 else 1, ndiv + 1):
                kpoint = np.rint((ki + (kf - ki) * j / ndiv)
                                 * divisor).astype(int)
                label = start if j == 0 else (end if j == ndiv else "")
                kpoints.append((label, kpoint, divisor))

    return kpoints


def write_klist_band(filename: str,
                     kpoints: List[Tuple[str, np.ndarray, int]],
                     emin: float = -8.0,
                     emax: float = 8.0) -> None:
    """
    Write the k-points to a case.klist_band file.

    The format is the fixed wien2k one, (A10, 4I5, 3F5.2), with the energy
    window only on the first line.

    Parameters
    ----------
    filename : string, required
               Filename of the case.klist_band file to write.
    kpoints  : list, required
               The k-points as returned by klist_band.
    emin     : float, optional
               Lower bound of the energy window written on the first line.
    emax     : float, optional
               Upper bound of the energy window written on the first line.
    """
    with open(filename, "w") as f:
        for ik, (label, kpoint, divisor) in enumerate(kpoints):
            fields = [kpoint[0], kpoint[1], kpoint[2], divisor]
            if any(len("{:d}".format(field)) > 5 for field in fields):
                raise ValueError(
                    "the k-point {} does not fit the 5 columns the klist_band "
                    "format gives it, try fewer k-points".format(fields))
            line = "{:<10}{:>5d}{:>5d}{:>5d}{:>5d}{:>5.1f}".format(
                label, kpoint[0], kpoint[1], kpoint[2], divisor, 2.0)
            if ik == 0:
                line += "{:>5.2f}{:>5.2f}    k-list generated by w2kplot".format(
                    emin, emax)
            f.write(line + "\n")
        f.write("END\n")
