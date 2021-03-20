
parser = argparse.ArgumentParser()

parser.add_argument("--code", type = str, choices = ["wien2k", "vasp"])
parser.add_argument("-b", "--bands", type = str)
parser.add_argument("--character", type = str)
parser.add_argument("--atoms", nargs="+", default=[])
parser.add_argument("--orbitals", nargs="+", default=[])
parser.add_argument("--fermi", default = None)
parser.add_argument("--ymin", default = None)
parser.add_argument("--xmin", default = None)
parser.add_argument("--xmax", default = None)
parser.add_argument("--ymax", default = None)
parser.add_argument("--kpath", nargs="+", default = [])
parser.add_argument("--klabels", nargs="+", default = [])
parser.add_argumnet("--colors", nargs = "+", default = [])
parser.add_argument("--weight_factor", nargs="+", default = [])
parser.add_argument("--save", default = None)

