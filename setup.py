import glob
import os
import shutil

from setuptools import setup
from setuptools.command.install import install



class InstallFiles(install):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.install_style()
        #atexit.register(install_style)

    def run(self):
        install.run(self)

    def install_style(self):
        import matplotlib
        # https://stackoverflow.com/questions/31559225/how-to-ship-or-distribute-a-matplotlib-stylesheet
        w2kplot_styles = glob.glob('style/*.mplstyle', recursive=True)
        mpl_dir = os.path.join(matplotlib.get_configdir(), "stylelib")
        if not os.path.exists(mpl_dir):
            os.makedirs(mpl_dir)
        print("installing w2kplot style sheet into", mpl_dir)
        for stylefile in w2kplot_styles:
            print(os.path.basename(stylefile))
            shutil.copy(stylefile,
                        os.path.join(mpl_dir, os.path.basename(stylefile)))

setup(name = "w2kplot",
      version = "0.0.5",
      author = "Harrison LaBollita",
      author_email = "hlabolli@asu.edu",
      description = "a Matplotlib wrapper written in Python for plotting DFT results from WIEN2k",
      url="https://github.com/harrisonlabollita/w2kplot",
      packages=['w2kplot'],
      license='MIT',
      install_requires =["numpy", "matplotlib"],
      cmdclass={'install': InstallFiles, },
      entry_points={
          "console_scripts": [
              "w2kplot-bands = w2kplot.cli.bandplot:main",
              ]
          },
      )
