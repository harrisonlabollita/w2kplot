from setuptools import setup

setup(name = "w2kplot",
      version = "0.0.2",
      author = "Harrison LaBollita",
      author_email = "hlabolli@asu.edu",
      description = "a Python wrapper to Matplotlib for plotting results from WIEN2k",
      packages=['w2kplot'],
      install_requires =["numpy", "matplotlib"])
