# -*- coding: utf-8 -*-

##########################################################################
#
# w2kplot: a thin Python wrapper around matplotlib
#
# Copyright (C) 2022 Harrison LaBollita
# Authors: H. LaBollita
#
# w2kplot is free software licensed under the terms of the MIT license.
#
##########################################################################

from w2kplot import Bands, band_plot
import matplotlib.pyplot as plt

import argparse


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-spag",
                        "--spaghetti",
                        default=None,
                        help="name of case.spaghetti/up/dn_ene file"
                        )

    parser.add_argument("-klist",
                        "--klistband",
                        default=None,
                        help="name of case.klist_band file"
                        )

    parser.add_argument("-eF",
                        "--fermienergy",
                        type=float,
                        default=0.0,
                        help="shift the Fermi energy by the amount fermienergy (units eV)"
                        )

    parser.add_argument("-c",
                        "--color",
                        type=str,
                        default="k",
                        help="color of the bands"
                        )

    parser.add_argument("-ls",
                        "--linestyle",
                        type=str,
                        default="-",
                        help="linestyle of ε(k)"
                        )

    parser.add_argument("-lw",
                        "--linewidth",
                        type=float,
                        default=1.5,
                        help="linewidth of ε(k)"
                        )

    parser.add_argument("--ymin",
                        default=-4,
                        type=float,
                        help="minimum of the y-axis."
                        )

    parser.add_argument("--ymax",
                        default=4,
                        type=float,
                        help="minimum of the y-axis."
                        )

    parser.add_argument("--save",
                        default=None,
                        help="save the bandstructure with the provided filename"
                        )

    return parser


def main():
    args = get_parser().parse_args()

    bands = Bands(spaghetti=args.spaghetti,
                  klist_band=args.klistband,
                  eF_shift=args.fermienergy
                  )

    band_plot(bands,
              ls=args.linestyle,
              color=args.color,
              lw=args.linewidth
              )

    plt.ylim(args.ymin, args.ymax)

    if args.save is not None:
        plt.savefig(args.save)
    else:
        plt.show()
