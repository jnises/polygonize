#/usr/bin/env python3

import sys
import tifffile
import numpy as np
import itertools

diagonal = ((0, 0, 0), (1, 1, 1))
tetrahedrons = [x + diagonal for x in (((0, 0, 1), (1, 0, 1)),
                                       ((0, 1, 0), (1, 1, 0)),
                                       ((0, 0, 1), (0, 1, 1)),
                                       ((1, 0, 0), (1, 1, 0)),
                                       ((0, 1, 0), (0, 1, 1)),
                                       ((1, 0, 0), (1, 0, 1)))]

def get_polygon(cube, isovalue):
    inside = cube > isovalue
    for t in tetrahedrons:
        for start, end in itertools.combinations(t, 2):
            if inside[start] != inside[end]:
                delta = np.array(end) - np.array(start)
                # do something more clever than 0.5
                yield np.array(start) + delta * 0.5

def polygonalize(indata, outfile, isovalue):
    assert len(indata.shape) == 3
    assert all(np.array(indata.shape) > 1)
    for z in range(indata.shape[0] - 1):
        for y in range(indata.shape[1] - 1):
            for x in range(indata.shape[2] - 1):
                cube = indata[z: z + 2, y: y + 2, x: x + 2].astype(float) / np.iinfo(indata.dtype).max
                insidecube = cube > isovalue
                if insidecube.any() and np.logical_not(insidecube).any():
                    polygon = [a + np.array((x, y, z)) for a in get_polygon(cube, isovalue)]
                    for vertex in polygon:
                        outfile.write('v {} {} {}\n'.format(*vertex))
                    if len(polygon):
                        outfile.write('f {}\n'.format(' '.join((str(a) for a in -1 - np.arange(len(polygon))))))
        sys.stdout.write('\r{}/{}'.format(z + 1, indata.shape[0] - 1))
    sys.stdout.write('\n')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('outfile')
    parser.add_argument('--isovalue', default = 0.5, type = float)
    args = parser.parse_args()
    indata = tifffile.imread(args.infile)
    with open(args.outfile, 'w') as outfile:
        polygonalize(indata, outfile, args.isovalue)