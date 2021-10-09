from setuptools import setup

setup(name = "spaghetti",
      version = "0.0.1",
      author = "Harrison LaBollita",
      author_email = "hlabolli@asu.edu",
      description = "a small plotting program written in python for plotting band structures calculated from wien2k and VASP",
      packages = ["spaghetti", "spaghetti.src"],
      install_requires =["numpy", "matplotlib", "numba"],
      scripts = ["spaghetti/src/spaghetti"])

