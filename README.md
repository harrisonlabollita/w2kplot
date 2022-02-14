<p align="center">
<a href="https://github.com/harrisonlabollita/w2kplot">
<img width = "300" src="logo.png" alt="w2kplot"/>
</a>
</p>


**w2kplot** is a Python wrapper built on [Matplotlib](https://matplotlib.org) to create publication quality plots from data generated from [WIEN2k](http://susi.theochem.tuwien.ac.at) density-functional theory (DFT) calculations.

**This program works! But it is still underdevelopment**

## Example

```python
	# plot basic band structure
	from w2kplot import Bands, band_plot
	
	plt.figure()
	dft_bands = Bands(spaghetti='case.spaghetti_ene', klist_band='case.klist_band')
	band_plot(dft_bands, 'k-', lw=1.5)
	plt.show()
```


**TO-DO**

- [x] basic library functions
- [x] density of states functionality
- [ ] fermi surface functionality


**PRs and feedback are welcome!**

## Installation

Currently, if you clone this repository and inside the repo issue the command you should be good to go!

```bash
    pip install -e .
```
