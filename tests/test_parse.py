import sys
sys.path.append("../spaghetti/")
from parse import parse

args = parse()
print(args.colors)
