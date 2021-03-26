#!/usr/bin/python3
def adjustArray(array):
    # The colors, orbitals, and weights arrays will need to be adjusted, they need to be a nested list instead of a flattened list
    newArray = []   
    subArray = []
    for ele in array:
        if ele != ",":
            subArray.append(ele)
        else:
            newArray.append(subArray)
            subArray = []
    return newArray



def parse():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--code", type = str, choices = ["wien2k", "vasp"], help = "Is the format wien2k or vasp?")
    parser.add_argument("-b", "--bands", type = str, help = "file containing the eigenvalues and kpoints aloong highsymmetry points. Example: case.spaghetti_ene")
    parser.add_argument("--character", default = None, help = "file containing band character. Example: case.qtl (wien2k) or PROCAR (Vasp)")
    parser.add_argument("--atoms", nargs="+", type = int, default=[], help = "if plotting band character indcies of atoms to plot the character for")
    parser.add_argument("--orbitals", nargs="+", default=[], help = "indices of orbitals to plot band character for")
    parser.add_argument("--fermi", type = float, default = None, help = "Fermi energy")
    parser.add_argument("--ymin", type = float, default = -1.5)
    parser.add_argument("--xmin", type = float, default = None)
    parser.add_argument("--xmax", type = float, default = None)
    parser.add_argument("--ymax", type = float, default = 1.5)
    parser.add_argument("--kpath", nargs="+", default = [], help = "points along the highsymmetry points")
    parser.add_argument("--klabels", nargs="+", default = [], help = "High symmetry points labels")
    parser.add_argument("--colors", nargs = "+", default = [], help = "colors to plot")
    parser.add_argument("--weight_factor", nargs="+", default = [], help = "weights multiply character by")
    parser.add_argument("--save", default = None, help = "option to save the image")

    args = parser.parse_args()
    args.colors = adjustArray(args.colors)
    args.orbitals = adjustArray(args.orbitals)
    args.weight_factor  = adjustArray(args.weight_factor)
    return args

