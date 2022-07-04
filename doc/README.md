## Documenation

w2kplot provides the user with various data objects: `Bands`, `FatBands`, `DensityOfStates`, which can then be passed to plotting functions `band_plot`, `fatband_plot`, `dos_plot`, which unravel the data contained in each object and create beautiful publication quality figures. We show case some examples [here](../examples/README.md).

### Bands
`Bands` is a `w2kplot` data object that contains the information about the band structure (extracted from case.spaghetti\_ene). This object takes the following keywords:

`spaghetti` (optional): filename of the case.spaghetti\_ene file.

`klist_band` (optional): filename of the case.klist\_band file.

If either of these files are not provided, w2kplot looks in the current directory for any files with the corresponding extensions.

### FatBands
`FatBands` is a child of the `Bands` object, but requires a few more inputs from the user in order to determine what to plot. They keyword arguments for this object are the following:

`atoms` (required): a list of atoms for which to plot the orbital character. 

`orbitals` (required): a list of lists, where there is a list of orbital indices corresponding to the list of atoms. The indices are taken from the `case.qtl` file.

`colors` (optional): a list of colors in the same format as the orbitals.
 
`weight` (optional): a scaling factor to scale the orbtial character of the bands. The multiplicty of each atom is considered.

`spaghetti` (optional): same as `Bands`.

`klist_band` (optional): same as `Bands`.

`qtl` (optional): a `case.qtl` file to obtain the orbital character. This file is obtained after running `x lapw2 -band -qtl`. If not provided, `w2kplot` looks in the current directory.

`eF` (optional): the Fermi energy in Rydbergs. If not provided, this value is taken from the `case.scf` file.

`struct` (optional): the structure file from WIEN2k. If not provided, `w2kplot` looks in the current directory.

### DensityOfStates

`DensityOfStates` is an object that contains the information about the density of states, which is obtained from `case.dosXev` files. The keyword arguments of this file are the following:

`dos` (optional): a list dosXev files. If not provided, `w2kplot` will obtain all the files in the current directory with this file format.

`dos_dict` (optional): a Python dictionary that matches each column in the dosXev files to a label name for creating a legend in the final plot. If not provided, this is built from the headers in the dosXev files.

### WannierBands

`WannierBands` is an object that contains the Wannier band data to be plot with or without the DFT band structure. Internally, the units are converted to match the units of Wien2k.

**TO-DO**
- [ ] 2D fermi surface functionality
- [ ] Fix import w2kplot style sheet
- [ ] add tests
