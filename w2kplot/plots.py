import matplotlib.pyplot as plt


def subplots(
        *args, 
        **kwargs
        ):

    add_inset = kwargs.pop('add_inset') if add_inset in kwargs else None
    fig, ax = plt.subplots(*args, **kwargs)

    return fig, ax
