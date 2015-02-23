#!/usr/bin/env python3

import tifffile
import numpy as np
import argparse

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('infile')
    args = p.parse_args()
    print('{}'.format(tifffile.imread(args.infile).shape))
