<p align="center">
<a href="https://github.com/harrisonlabollita/w2kplot">
<img width = "450" src="doc/logo.png" alt="w2kplot"/>
</a>
</p>

<div align="center">

![tests](https://github.com/harrisonlabollita/w2kplot/actions/workflows/test.yml/badge.svg)
![issues](https://img.shields.io/github/issues/harrisonlabollita/w2kplot)
![forks](https://img.shields.io/github/forks/harrisonlabollita/w2kplot)
![stars](https://img.shields.io/github/stars/harrisonlabollita/w2kplot)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
![license](https://img.shields.io/github/license/harrisonlabollita/w2kplot)
	
</div>

## Overview

**w2kplot** is a [Matplotlib](https://matplotlib.org) wrapper written in Python to create publication quality plots from data generated from the [WIEN2k](http://susi.theochem.tuwien.ac.at) density-functional theory (DFT) code.

- [Getting Started](#started)
- [Commmand Line Interface](#commandline)
- [Installation](#installation)
- [Documentation](#documentation)
- [Contributing](#contributing)


<a name="started"></a>
## Getting Started
w2kplot is designed to be intuitive for anyone familiar with the matplotlib library. It is seamlessly integrated, such that the user only has to worry about showcasing their results, not how to showcase their resutls. For example, we can plot the band structure from a WIEN2k calculation in the directory `case` with just a few lines of Python code.

```python
	# plot basic band structure
	from w2kplot.bands import Bands, band_plot
	
	plt.figure()
	dft_bands = Bands(spaghetti='case.spaghetti_ene', klist_band='case.klist_band')
	band_plot(dft_bands, 'k-', lw=1.5)
	plt.show()
```

For more examples, see [examples](examples/)!

<a name="commandline"></a>
## Command Line Interface (CLI)
w2kplot has a command line interface for quickly viewing results and testing. A band structure can be plotted from the case directory by executing ``w2kplot-bands``. Similarily, the orbital character ("fatbands") can be generated from ``w2kplot-fatbands``. The entire list of options that allow you to drive these two tools are shown below.

```bash
w2kplot-bands -h

usage: w2kplot-bands [-h] [-spag SPAGHETTI] [-klist KLISTBAND] [-eF FERMIENERGY] [-c COLOR] [-ls LINESTYLE] [-lw LINEWIDTH] [--ymin YMIN] [--ymax YMAX] [--save SAVE]

optional arguments:
  -h, --help            show this help message and exit
  -spag SPAGHETTI, --spaghetti SPAGHETTI
                        name of case.spaghetti/up/dn_ene file
  -klist KLISTBAND, --klistband KLISTBAND
                        name of case.klist_band file
  -eF FERMIENERGY, --fermienergy FERMIENERGY
                        shift the Fermi energy by the amount fermienergy (units eV)
  -c COLOR, --color COLOR
                        color of the bands
  -ls LINESTYLE, --linestyle LINESTYLE
                        linestyle of ε(k)
  -lw LINEWIDTH, --linewidth LINEWIDTH
                        linewidth of ε(k)
  --ymin YMIN           minimum of the y-axis.
  --ymax YMAX           minimum of the y-axis.
  --save SAVE           save the bandstructure with the provided filenameusage: w2kplot-bands [-h] [-spag SPAGHETTI] [-klist KLISTBAND] [-eF FERMIENERGY] [-c COLOR] [-ls LINESTYLE] [-lw LINEWIDTH] [--ymin YMIN] [--ymax YMAX] [--save SAVE]

optional arguments:
  -h, --help            show this help message and exit
  -spag SPAGHETTI, --spaghetti SPAGHETTI
                        name of case.spaghetti/up/dn_ene file
  -klist KLISTBAND, --klistband KLISTBAND
                        name of case.klist_band file
  -eF FERMIENERGY, --fermienergy FERMIENERGY
                        shift the Fermi energy by the amount fermienergy (units eV)
  -c COLOR, --color COLOR
                        color of the bands
  -ls LINESTYLE, --linestyle LINESTYLE
                        linestyle of ε(k)
  -lw LINEWIDTH, --linewidth LINEWIDTH
                        linewidth of ε(k)
  --ymin YMIN           minimum of the y-axis.
  --ymax YMAX           minimum of the y-axis.
  --save SAVE           save the bandstructure with the provided filename
```

```bash
w2kplot-fatbands -h

usage: w2kplot-fatbands [-h] --atoms ATOMS [ATOMS ...] -orb ORBITALS [ORBITALS ...] [-struct STRUCTURE] [--qtl QTL] [--ef EF] [--weight WEIGHT] [-spag SPAGHETTI]
                        [-klist KLISTBAND] [-eF FERMIENERGY] [--colors COLORS [COLORS ...]] [-c COLOR] [-ls LINESTYLE] [-lw LINEWIDTH] [--ymin YMIN] [--ymax YMAX]
                        [--save SAVE]

optional arguments:
  -h, --help            show this help message and exit
  --atoms ATOMS [ATOMS ...]
  -orb ORBITALS [ORBITALS ...], --orbitals ORBITALS [ORBITALS ...]
  -struct STRUCTURE, --structure STRUCTURE
  --qtl QTL
  --ef EF
  --weight WEIGHT       scaling factor for the size of the orbital character.
  -spag SPAGHETTI, --spaghetti SPAGHETTI
                        name of case.spaghetti/up/dn_ene file
  -klist KLISTBAND, --klistband KLISTBAND
                        name of case.klist_band file
  -eF FERMIENERGY, --fermienergy FERMIENERGY
                        shift the Fermi energy by the amount Fermi energy (units eV)
  --colors COLORS [COLORS ...]
                        colors of the orbitals
  -c COLOR, --color COLOR
                        color of the bands
  -ls LINESTYLE, --linestyle LINESTYLE
                        linestyle of ε(k)
  -lw LINEWIDTH, --linewidth LINEWIDTH
                        linewidth of ε(k)
  --ymin YMIN           minimum of the y-axis.
  --ymax YMAX           minimum of the y-axis.
  --save SAVE           save the bandstructure with the provided filename
```


<a name="installation"></a>
## Installation

Currently, installation procedure
```bash
    git clone https://github.com/harrisonlabollita/w2kplot.git
    cd w2kplot
    pip install -e .
```

<a name="documentation"><a/>
## Documenation

w2kplot provides the user with various Python class objects: `Bands`, `FatBands`, `DensityOfStates`, etc. which are then passed to the matplotlib plotting functions provided by this package: `band_plot`, `fatband_plot`, `dos_plot` to create publication quality figures with minimal effort. We show case some examples [here](examples/README.md).

### Bands
`Bands` is a `w2kplot` data object that contains the information about the band structure (extracted from case.spaghetti\_ene). This object takes the following keywords:

- `spaghetti` (optional): filename of the case.spaghetti\_ene file.

- `klist_band` (optional): filename of the case.klist\_band file.

If either of these files are not provided, w2kplot looks in the current directory for any files with the corresponding extensions. In general, it is always safest to provide the exact file that you would like the program to parse, otherwise, this can lead to some ambiguity and potentially spurious results.

### FatBands
`FatBands` is another data object that is inherited from the `Bands` object, but requires a few more inputs from the user in order to determine how to plot the fatbands. The keyword arguments for this object are the following:

- `atoms` (required): a list of atoms for which to plot the orbital character. 

- `orbitals` (required): a list of lists, where there is a list of orbital indices corresponding to the list of atoms. The indices are taken from the `case.qtl` file.

- `colors` (optional): a list of colors in the same format as the orbitals.
 
- `weight` (optional): a scaling factor to scale the orbtial character of the bands. The multiplicty of each atom is considered.

- `spaghetti` (optional): same as `Bands`.

- `klist_band` (optional): same as `Bands`.

- `qtl` (optional): a `case.qtl` file to obtain the orbital character. This file is obtained after running `x lapw2 -band -qtl`. If not provided, `w2kplot` looks in the current directory.

- `eF` (optional): the Fermi energy in Rydbergs. If not provided, this value is taken from the `case.scf` file.

- `struct` (optional): the structure file from WIEN2k. If not provided, `w2kplot` looks in the current directory.

### WannierBands
`WannierBands` is an object that contains the Wannier band data to be plot with or without the DFT band structure. Internally, the units are converted to match the units of Wien2k.

### DensityOfStates (DOS)
`DensityOfStates` with alias `DOS` wraps a Wien2k dos file. Still underdevelopment. We provide plotting functions for density of states with the function `dos_plot`, which has multiple styles (`dos_style`). 


<a name="contributing"><a/>	
## Contributing
Contributions are welcome! Here's how you can get involved:

1. Fork the repository.
2. Create a new branch: ``git checkout -b feature-new-feature``.
3. Make your changes and commit them: ``git commit -m 'Add new feature'``.
4. Push to the branch: ``git push origin feature-new-feature``.
5. Create a pull request detailing your changes.
