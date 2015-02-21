#/usr/bin/env python3

import sys
import tifffile
import h5py

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('usage: {} infile outfile'.format(sys.argv[0]))
    with h5py.File(sys.argv[2], 'w', libver = 'latest') as outfile:
        outfile.create_dataset('volume', data = tifffile.imread(sys.argv[1]), chunks = True, compression = 'gzip')
