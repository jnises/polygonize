#!/usr/bin/env python3

import h5py
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
    with h5py.File(args.infile, 'r') as infile, h5py.File(args.outfile, 'w', libver = 'latest') as outfile:
        for dataset in infile.values():
            outdata = outfile.create_dataset(dataset.name, data = scipy.ndimage.interpolation.zoom(dataset, (args.z, args.y, args.x)), chunks = True if dataset.chunks else None, compression = dataset.compression)
