from matplotlib.lines import Line2D
import numpy as np

make_label = lambda **kwargs: Line2D([0], [0], **kwargs)


def kpath_gen(segments, N=100):
    segments = [(np.asarray(a), np.asarray(b)) for (a, b) in segments]
    x = np.linspace(0, 1, N)
    kvecs = np.vstack([ki[None, :] + x[:, None]*(kf-ki)[None, :]
                       for ki, kf in paths])
    kvecs = np.asarray(np.ceil(kvecs*len(kvecs)), dtype=int)
    div = len(kvecs)
    drop = np.array([N*i for i in range(1, len(segments))])
    kvecs = np.delete(kvecs, drop, axis=0)
    return kvecs, div


def fs_gen(UL, LR, Z, kz=0.0, N=25):
    def k_path(paths):
        x = np.linspace(0, 1, N)
        kvecs = [ki[None, :] + x[:, None]*(kf-ki)[None, :] for ki, kf in paths]
        return np.vstack(kvecs).astype(int)
    kpts = []
    for ik in range(N):
        seg = [(UL*ik/(N-1) + kz*Z, LR + UL*ik/(N-1) + kz*Z)]
        kpts.append(k_path(seg))
    return np.vstack(kpts)
