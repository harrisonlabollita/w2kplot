import glob, sys
class struct:
    """this is a wien2k structure class that contains the information 
       we need about about the crystal structure to plot the bands.
    """
    def __init__(self):
        if len(glob.glob("*.struct")) > 0:
            self.load()
        else:
            print("Couldn't find a struct file...quitting")
            sys.exit(1)

    def load(self):
        contents=open(glob.glob("*.struct")[0]).readlines()
        self.filename=glob.glob("*.struct")[0]
        self.nat=int(contents[1].split()[2])
        self.spg=int(contents[1].split()[3])
        iatom=list(range(1,self.nat+1))
        mults=[int(line.split()[1]) for line in contents if "MULT" in line]
        specs=[str(line.split()[0]) for line in contents if "NPT" in line]
        self.atoms={}
        assert len(mults)==len(specs), "Did not parse the struct file correctly!"
        assert len(iatom)==len(specs), "Did not parse the struct file correctly!"
        for a in range(self.nat):
            self.atoms[a]=[specs[a], mults[a]]
