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
- [Installation](#installation)
- [Documentation](#documentation)
- [Contributing](#contributing)


<a name="started"></a>
## Getting Started
w2kplot is designed to be intuitive for anyone familiar with the matplotlib library. It is seamlessly integrated, such that the user only has to worry about showcasing their results, not how to showcase their resutls. For example, we can plot the band structure from a WIEN2k calculation in the directory `case` with just a few lines of Python code.

```python
	# plot basic band structure
	from w2kplot import Bands, band_plot
	
	plt.figure()
	dft_bands = Bands(spaghetti='case.spaghetti_ene', klist_band='case.klist_band')
	band_plot(dft_bands, 'k-', lw=1.5)
	plt.show()
```

For more examples, see [examples](examples/)!

<a name="installation"></a>
## Installation

Currently, this is the only way to install w2kplot
```bash
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

### DensityOfStates

`DensityOfStates` is an object that contains the information about the density of states, which is obtained from `case.dosXev` files. The keyword arguments of this file are the following:

- `dos` (optional): a list dosXev files. If not provided, `w2kplot` will obtain all the files in the current directory with this file format.

- `dos_dict` (optional): a Python dictionary that matches each column in the dosXev files to a label name for creating a legend in the final plot. If not provided, this is built from the headers in the dosXev files.

### WannierBands

`WannierBands` is an object that contains the Wannier band data to be plot with or without the DFT band structure. Internally, the units are converted to match the units of Wien2k.

<a name="contributing"><a/>	
## Contributing

Pull requests and contributions are welcome! On my end, I plan to implement a way to visualize the Fermi surface.
