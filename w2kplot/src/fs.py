#!/usr/bin/env python
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from matplotlib import colors
plt.style.use("publish")


def kpoints_energies(filename,eF=0.7461563713,window=[-0.025,0.025]):
    lines = open(filename).readlines()
    vkl = []
    energies=[]
    for (i, line) in enumerate(lines):
        if len(line) == 88:
            kpt = [float(line.split()[i]) for i in range(3)]
            vkl.append(kpt)
            j = i+1
            Ek=[]
            while len(lines[j]) == 37 and j < len(lines)-1:
                E=(float(lines[j].strip().split()[-1])-eF)*13.6
                if E > window[0] and E < window[1]:
                    Ek.append(E)
                j += 1
            energies.append(sum(Ek))
    print("no k-points : {}".format(len(vkl)))
    assert len(vkl) == len(energies), "The number of kpoints and the number of Ek do not match"
    return vkl,energies


def symmetries(struct):
    lines = open(struct).readlines()
    start = 0
    for (i, line) in enumerate(lines):
        if "NUMBER OF" in line:
            num_ops=int(line.split()[0])
            start=i+1
            break
    symm_ops=[]
    for line in range(start, len(lines),4):
        rot_mat=np.zeros((3,3),dtype=np.int_)
        for row in range(3):
            curr_line=lines[line+row].strip().split()[:-1]
            if len(curr_line) == 2:
                if curr_line[0] == "0-1":
                    rot_mat[:,row]=np.array([0,-1,0],dtype=np.int_)
                elif curr_line[1] == "0-1":
                    rot_mat[:,row] = np.array([0, 0, -1],dtype=np.int_)
                else:
                    print("This is an edge case I wasn't expecting. Exiting...")
                    sys.exit(1)
            else:
                rot_mat[:,row] = np.array(curr_line, dtype=np.int_)
        symm_ops.append(rot_mat)
    assert len(symm_ops) == num_ops, "The number of symmetry operations in file does not match the number parsed."
    return symm_ops


def fs(vkl, energies, symlatt):
    v = np.zeros(3, np.float_)
    vkc = np.zeros([len(vkl), 3], np.float_)
    iknr = np.arange(len(vkl))
    for isym in range(len(symlatt)):
        for ik in range(len(vkl)):
            v[:] = np.matmul(symlatt[isym][:, :], vkl[ik])
            vkc = np.vstack((vkc, v))
            iknr = np.append(iknr, ik)
    [vkc, ind] = np.unique(vkc, return_index = True, axis = 0)
    iknr = iknr[ind]
    iksrt = np.lexsort(([vkc[:, i] for i in range(0, vkc.shape[1], 1)]))
    vkc = vkc[iksrt]
    iknr = iknr[iksrt]
    shift=1
    x = []
    y = []
    Esurf = np.zeros(len(vkc))
    for ik in range(len(vkc)):
        x.append(vkc[ik, 0])
        y.append(vkc[ik, 1])
        jk = iknr[ik]
        Esurf[ik] += energies[jk]
    for e in range(len(Esurf)):
        if Esurf[e] != 0:
            Esurf[e] = 1

    #kx, ky = np.meshgrid(np.linspace(-0.5, 0.5, 1000), np.linspace(-0.5, 0.5, 1000))
    #Esurf = griddata((x, y), Esurf, (kx, ky), method = "cubic")
    fig, ax = plt.subplots(figsize=(6, 6))
    plt.set_cmap("Greys")
    ax.scatter(x,y,s=50,c=Esurf, marker="s")
    #norm = colors.LogNorm(vmin=np.min(Esurf), vmax=np.max(Esurf))
    #ax.pcolor(kx, ky, Esurf, norm=norm, shading = "auto", rasterized=True)
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xticks([-0.5, 0.5])
    ax.set_yticks([0.5])
    ax.set_xticklabels([r"-$\pi$", r"$\pi$"])
    ax.set_yticklabels([ r"$\pi$"])
    ax.tick_params('both', length=0)
    #ax.axis("off")


def main(case):
    symlatt = symmetries(case+'.struct')
    vkl, energies = kpoints_energies(case+'.energy')
    fs(vkl, energies, symlatt)


if __name__ == "__main__":
    main(sys.argv[1])
