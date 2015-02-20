#/usr/bin/env python3

import tifffile
import numpy as np
import scipy.ndimage.interpolation
import argparse

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('infile')
    p.add_argument('outfile')
    p.add_argument('-x', default = 1, type = float)
    p.add_argument('-y', default = 1, type = float)
    p.add_argument('-z', default = 1, type = float)
    args = p.parse_args()
    tifffile.imsave(args.outfile, scipy.ndimage.interpolation.zoom(tifffile.imread(args.infile), (args.x, args.y, args.z)))
