def parse():
    import argpase

    parser = argparse.ArgumentParser()

    parser.add_argument("--code", type = str, choices = ["wien2k", "vasp"], help = "Is the format wien2k or vasp?")
    parser.add_argument("-b", "--bands", type = str, help = "file containing the eigenvalues and kpoints aloong highsymmetry points. Example: case.spaghetti_ene")
    parser.add_argument("--character", default = None, help = "file containing band character. Example: case.qtl (wien2k) or PROCAR (Vasp)")
    parser.add_argument("--atoms", nargs="+", default=[], help = "if plotting band character indcies of atoms to plot the character for")
    parser.add_argument("--orbitals", nargs="+", default=[], help = "indices of orbitals to plot band character for")
    parser.add_argument("--fermi", default = None, help = "Fermi energy")
    parser.add_argument("--ymin", default = None)
    parser.add_argument("--xmin", default = None)
    parser.add_argument("--xmax", default = None)
    parser.add_argument("--ymax", default = None)
    parser.add_argument("--kpath", nargs="+", default = [], help = "points along the highsymmetry points")
    parser.add_argument("--klabels", nargs="+", default = [], help = "High symmetry points labels")
    parser.add_argumnet("--colors", nargs = "+", default = [], help = "colors to plot")
    parser.add_argument("--weight_factor", nargs="+", default = [], help = "weights multiply character by")
    parser.add_argument("--save", default = None, help = "option to save the image")

    args = parser.parse_args()
    return args

