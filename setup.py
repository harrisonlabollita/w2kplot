
from setuptools import setup



setup(name="w2kplot",
      version="0.1.1",
      author="Harrison LaBollita",
      author_email="harrisonlabollita@gmail.com",
      description="a Matplotlib wrapper written in Python for plotting DFT results from WIEN2k",
      url="https://github.com/harrisonlabollita/w2kplot",
      packages=['w2kplot'],
      license='MIT',
      install_requires=["numpy", "matplotlib"],
      package_data = {'w2kplot' : ['w2kplot_base.mplstyle', 
                                   'w2kplot_bands.mplstyle']
                                   },
      scripts = ["w2kplot/cli/w2kplot-bands", "w2kplot/cli/w2kplot-fatbands"]
      )
