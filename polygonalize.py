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

_optimize = False
if _optimize:
    try:
        from numba import jit
    except ImportError:
        sys.stderr.write('unable to import numba, things will be slow\n')
        def jit(func):
            return func
else:
    def jit(func):
        return func
diagonal = ((0, 0, 0), (1, 1, 1))
tetrahedrons = [x + diagonal for x in (((0, 0, 1), (1, 0, 1)),
                                       ((0, 1, 0), (1, 1, 0)),
                                       ((0, 0, 1), (0, 1, 1)),
                                       ((1, 0, 0), (1, 1, 0)),
                                       ((0, 1, 0), (0, 1, 1)),
                                       ((1, 0, 0), (1, 0, 1)))]

@jit
def _calculate_vertex(start, end, cube, isovalue):
    if cube[start] < cube[end]:
        value = (isovalue - cube[start]) / (cube[end] - cube[start])
    else:
        value = 1 - (isovalue - cube[end]) / (cube[start] - cube[end])
    return np.array(start) + (np.array(end) - np.array(start)) * value

@jit
def _get_polygons(cube, isovalue):
    insidecube = cube > isovalue
    vertices = []
    for t in tetrahedrons:
        inside = []
        outside = []
        for s in t:
            if insidecube[s]:
                inside.append(s)
            else:
                outside.append(s)
        if len(inside) == 2:
            vertices.append([_calculate_vertex(inside[0], outside[0], cube, isovalue),
                             _calculate_vertex(inside[0], outside[1], cube, isovalue),
                             _calculate_vertex(inside[1], outside[1], cube, isovalue),
                             _calculate_vertex(inside[1], outside[0], cube, isovalue)])
        elif len(inside) == 1:
            vertices.append([_calculate_vertex(inside[0], outside[0], cube, isovalue),
                             _calculate_vertex(inside[0], outside[1], cube, isovalue),
                             _calculate_vertex(inside[0], outside[2], cube, isovalue)])
        elif len(inside) == 3:
            vertices.append([_calculate_vertex(outside[0], inside[0], cube, isovalue),
                             _calculate_vertex(outside[0], inside[1], cube, isovalue),
                             _calculate_vertex(outside[0], inside[2], cube, isovalue)])
    return vertices

@jit
def _polygonize_layer(layer, isovalue):
    floatlayer = layer.astype(float) / np.iinfo(layer.dtype).max
    vertices = []
    faces = []
    for y in range(layer.shape[1] - 1):
        for x in range(layer.shape[2] - 1):
            cube = floatlayer[:, y: y + 2, x: x + 2]
            insidecube = cube > isovalue
            if insidecube.any() and np.logical_not(insidecube).any():
                for polygon in _get_polygons(cube, isovalue):
                    polygon += np.array((0, y, x))
                    vertices.extend(polygon)
                    if len(polygon):
                        faces.append(len(vertices) - np.arange(len(polygon)))
    # TODO remove duplicate vertices
    return (vertices, faces)

def polygonalize(indata, outfile, isovalue):
    assert len(indata.shape) == 3
    assert all(np.array(indata.shape) > 1)
    vertexnumber = 0
    for z in range(indata.shape[0] - 1):
        vertices, faces = _polygonize_layer(indata[z: z + 2], isovalue)
        for vertex in vertices:
            outfile.write('v {} {} {}\n'.format(vertex[2], vertex[1], vertex[0] + z))
        for face in faces:
            outfile.write('f {}\n'.format(' '.join((str(vertexnumber - a) for a in range(face.shape[0])))))
        vertexnumber += len(vertices)
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
