import numpy as np
import matplotlib.pyplot as plt


def construct_lattice(a, b, c, alpha, beta, gamma):
    
    r1 = np.array([a, 0, 0])
    r2 = b * np.array([np.cos(gamma), np.sin(gamma), 0])

    xcom = np.cos(beta)
    ycom = (np.cos(alpha) - np.cos(beta)*np.cos(gamma))/np.sin(gamma)
    zcom = np.sqrt(1 - np.cos(beta)*np.cos(beta) - ycom*ycom)
    r3 = c * np.array([xcom, ycom, zcom])
    return np.vstack([r1, r2, r3]).transpose()


def symmetry(struct):
    f = open(struct, "r")
    lines = f.readlines()
    for i in range(len(lines)):
        if "NUMBER" in lines[i]:
            matrices = lines[i+1:]
    rows = []
    for m in range(len(matrices)):
        row = []
        for el in matrices[m].split():
            try:
                row.append(float(el))
            except:
                if el == "1-1":
                    row.append(1)
                    row.append(-1)
                elif el == "0-1":
                    row.append(0)
                    row.append(-1)
                else:
                    print("edge case that I haven't run into yet")
        if len(row) == 4:
            rows.append(row[:-1])
    
    symmetries = []   
    for r in range(0, len(rows), 3):
        tmp = rows[r:r+3]
        symm = np.array(tmp).reshape(3, 3)
        symmetries.append(symm)
    print("Found {} symmetries".format(len(symmetries)))
    return symmetries


def energy(file):
    lines = open(file).readlines()
    vkl = []
    bands = []
    for ll in lines:
        if len(ll) == 88:
            kpt = [float(ll.split()[i]) for i in range(3)]
            vkl.append(kpt)
        elif len(ll) == 37:
            e = float(ll.split()[1])
            bands.append(e)
    print("num. k-points : {}".format(len(vkl)))
    bands = np.array(bands).reshape(len(vkl), int(len(bands)/len(vkl))).transpose()
    print("num bands     : {}".format(bands.shape[0]))
    return vkl, bands


def fermi_surface(latt, vkl, bands, symmetries, eF):
    
    Ry2eV = 13.6

    recp = 2 * np.pi * np.linalg.inv(latt).T

    v = np.zeros(3, np.float_)

    vkc = np.zeros((len(vkl), 3), np.float_)
    
    for ik in range(len(vkl)):
        vkc[ik, :] = np.matmul(recp, vkl[ik])

    iknr = np.arange(len(vkl))

    for isym in range(len(symmetries)):
        
        for ik in range(len(vkl)):
            
            v[:] = np.matmul(symmetries[isym][:, :], vkl[ik])
            
            v[:] = np.matmul(recp, v[:])

            vkc = np.vstack((vkc, v))
            
            iknr = np.append(iknr, ik)

    [vkc, ind] = np.unique(vkc, return_index=True, axis=0)
    
    iknr = iknr[ind]
    
    iksrt = np.lexsort(([vkc[:, i] for i in range(0, vkc.shape[1], 1)]))
    
    vkc   = vkc[iksrt]
    
    iknr  = iknr[iksrt]

    # bands -= eF
    # bands *= Ry2eV

    return vkc, iknr, bands


if __name__ == "__main__":
    a = 10.383856
    b = 10.383856
    c = 17.590516
    alpha = np.pi/2
    beta = np.pi/2
    gamma = 2*np.pi/3.
    struct = "Cs35_nm_dft.struct"
    ene    = "Cs35_nm_dft.energy"
    eF = 0.4717

    latt = construct_lattice(a, b, c, alpha, beta, gamma)
    print(latt)
    symmetries = symmetry(struct)
    vkl, bands = energy(ene)
    vkc, iknr, bands = fermi_surface(latt, vkl, bands, symmetries, eF)
    kx = [vkc[ik][0] for ik in range(len(vkc))]
    ky = [vkc[ik][1] for ik in range(len(vkc))]
    print(bands.shape)
    surf = [13.6*(bands[68][iknr[ik]]-eF) for ik in range(len(vkc))]
    plt.figure()
    plt.set_cmap("viridis")
    plt.scatter(kx, ky, s=10, c=surf)
    plt.colorbar()
    plt.show()

