#!/usr/bin/env python3

'''
polygonalize volume data
author: Joel Nises
'''

import sys
import h5py
import numpy as np
import itertools
import tifffile

diagonal = ((0, 0, 0), (1, 1, 1))
tetrahedrons = [x + diagonal for x in (((0, 0, 1), (1, 0, 1)),
                                       ((0, 1, 0), (1, 1, 0)),
                                       ((0, 0, 1), (0, 1, 1)),
                                       ((1, 0, 0), (1, 1, 0)),
                                       ((0, 1, 0), (0, 1, 1)),
                                       ((1, 0, 0), (1, 0, 1)))]

def get_polygons(cube, isovalue):
    insidecube = cube > isovalue
    def calculate_vertex(start, end):
        if cube[start] < cube[end]:
            value = (isovalue - cube[start]) / (cube[end] - cube[start])
        else:
            value = 1 - (isovalue - cube[end]) / (cube[start] - cube[end])
        return np.array(start) + (np.array(end) - np.array(start)) * value
    for t in tetrahedrons:
        inside = [s for s in t if insidecube[s]]
        outside = [s for s in t if not insidecube[s]]
        if len(inside) == 2:
            yield [calculate_vertex(inside[0], outside[0]),
                   calculate_vertex(inside[0], outside[1]),
                   calculate_vertex(inside[1], outside[1]),
                   calculate_vertex(inside[1], outside[0])]
        elif len(inside) == 1:
            yield [calculate_vertex(inside[0], outside[0]),
                   calculate_vertex(inside[0], outside[1]),
                   calculate_vertex(inside[0], outside[2])]
        elif len(inside) == 3:
            yield [calculate_vertex(outside[0], inside[0]),
                   calculate_vertex(outside[0], inside[1]),
                   calculate_vertex(outside[0], inside[2])]

def polygonalize(indata, outfile, isovalue):
    assert len(indata.shape) == 3
    assert all(np.array(indata.shape) > 1)
    vertexnumber = 0
    for z in range(indata.shape[0] - 1):
        for y in range(indata.shape[1] - 1):
            for x in range(indata.shape[2] - 1):
                cube = indata[z: z + 2, y: y + 2, x: x + 2].astype(float) / np.iinfo(indata.dtype).max
                insidecube = cube > isovalue
                if insidecube.any() and np.logical_not(insidecube).any():
                    for polygon in (a + np.array((z, y, x)) for a in get_polygons(cube, isovalue)):
                        for vertex in polygon:
                            outfile.write('v {} {} {}\n'.format(vertex[2], vertex[1], vertex[0]))
                            vertexnumber += 1
                        if len(polygon):
                            outfile.write('f {}\n'.format(' '.join((str(vertexnumber - a) for a in range(len(polygon))))))
        sys.stdout.write('\r{}/{}'.format(z + 1, indata.shape[0] - 1))
    sys.stdout.write('\n')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('outfile')
    parser.add_argument('--isovalue', default = 0.5, type = float)
    args = parser.parse_args()
    infile = None
    if args.infile.endswith('.hdf5'):
        infile = h5py.File(args.infile, 'r')
        indata = list(infile.values())[0]
    else:
        indata = tifffile.imread(args.infile)
    try:
        with open(args.outfile, 'w') as outfile:
            polygonalize(indata, outfile, args.isovalue)
    finally:
        if infile:
            infile.close()
