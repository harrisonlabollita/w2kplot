Spaghetti
=========

**Spaghetti** is a Python program to create publication quality band structure plots from [Wien2k](http://susi.theochem.tuwien.ac.at) density-functional theory (DFT) calculations. The user simply runs the program inside the directory with the required files from Wien2k and it takes care of the rest! 



**Warning: This program _works_! But only the minimal functionalilty right now! More to come.**

## Example
Inside a directory with files: case.bands.agr and case.spaghetti\_ene (minimal files), simply type

```bash
	spaghetti --switch bands
```
This will plot the E(k) vs the high-symmetry k-path detected from the case.bands.agr. The user can provide this information as well. For fatbands,

```bash
	spaghetti --init --switch fatbands
```
The init flag creates the ``spaghetti.init`` file which tells the progam which atom and orbitals you would like to plot the fatbands for. To use this feature, you must provide the case.qtl (for orbital content), case.struct (to create init file), and case.scf (to grab the Fermi energy).


**TO-DO**
- [x] basic band structure program basically done
- [ ] new features
	- make nice legend
	- speed up qtl loops
- [ ] complete Fermi surface slices program
	- generate klistband file
        - create a job.sh file to run wien2k
	3. program to plot the resulting Fermi surface slice
**PRs and feedback are welcome!**
