from setuptools import setup

setup(name = "w2kplot",
      version = "0.0.1",
      author = "Harrison LaBollita",
      author_email = "hlabolli@asu.edu",
      description = "a small plotting program written in Python for post processing results in Wien2k",
      packages = ["w2kplot", "w2kplot.src"],
      install_requires =["numpy", "matplotlib"],
      scripts = ["w2kplot/src/w2kplot"])

