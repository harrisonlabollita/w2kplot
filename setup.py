from setuptools import setup

setup(name = "w2kplot",
      version = "0.0.3",
      author = "Harrison LaBollita",
      author_email = "hlabolli@asu.edu",
      description = "a Matplotlib wrapper written in Python for plotting DFT results from WIEN2k",
      url="https://github.com/harrisonlabollita/w2kplot",
      packages=['w2kplot'],
      license='MIT',
      install_requires =["numpy", "matplotlib"])
