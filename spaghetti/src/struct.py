import glob
class struct:
    """this is a wien2k structure class that contains the information 
       we need about about the crystal structure to plot the bands.
    """
    def __init__(self):
        self.load()

    def load(self):
        contents=open(glob.glob("*.struct")[0]).readlines()
        self.nat=int(contents[1].split()[1])
        self.spg=int(contents[1].split()[2])
        iatom=list(range(1,nat+1))
        mults=[int(line.split()[1]) for line in contents if "MULT" in line]
        specs=[str(line.split()[0]) for line in contents if "NPT" in line]
        self.atoms={}
        assert len(mults)==len(specs), "Did not parse the struct file correctly!"
        assert len(iatom)==len(specs), "Did not parse the struct file correctly!"
        for a in range(self.nat):
            self.atoms[a]=[specs[a], mults[a]]
