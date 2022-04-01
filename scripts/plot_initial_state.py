#!/usr/bin/env python
"""
This script creates histogram plots of the initial condition.
"""
# import modules
import xarray
import numpy as np
import math
import argparse
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


def main():
    # parser
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-i', '--input_file_name', dest='input_file_name',
        default='ocean.nc',
        help='MPAS file name for input of initial state.')
    parser.add_argument(
        '-o', '--output_file_name', dest='output_file_name',
        default='initial_state.png',
        help='File name for output image.')
    args = parser.parse_args()

    # load mesh variables
    chunks = {'nCells': 32768, 'nEdges': 32768}
    ds = xarray.open_dataset(args.input_file_name, chunks=chunks)
    nCells = ds.sizes['nCells']
    nEdges = ds.sizes['nEdges']
    nVertLevels = ds.sizes['nVertLevels']

    fig = plt.figure()
    fig.set_size_inches(16.0, 12.0)
    plt.clf()

    print('plotting histograms of the initial condition')
    print('see: init/initial_state/initial_state.png')
    d = datetime.datetime.today()
    txt = \
        'MPAS-Ocean initial state\n' + \
        'date: {}\n'.format(d.strftime('%m/%d/%Y')) + \
        'number cells: {}\n'.format(nCells) + \
        'number cells, millions: {:6.3f}\n'.format(nCells / 1.e6) + \
        'number layers: {}\n\n'.format(nVertLevels) + \
        '  min val   max val  variable name\n'

    plt.subplot(3, 3, 2)
    varName = 'bottomDepth'
    var = ds[varName]
    xarray.plot.hist(var, bins=100, log=True)
    plt.ylabel('frequency')
    plt.xlabel(varName)
    txt = '{}{:9.2e} {:9.2e} {}\n'.format(txt, var.min().values, 
                                          var.max().values, varName)

    cellsOnEdge = ds['cellsOnEdge'].values - 1
    cellMask = np.zeros((nCells, nVertLevels), bool)
    edgeMask = np.zeros((nEdges, nVertLevels), bool)
    for k in range(nVertLevels):
        cellMask[:, k] = k <= 1
        cell0 = cellsOnEdge[:, 0]
        cell1 = cellsOnEdge[:, 1]
        edgeMask[:, k] = np.logical_and(np.logical_and(cellMask[cell0, k],
                                                       cellMask[cell1, k]),
                                        np.logical_and(cell0 >= 0,
                                                       cell1 >= 0))
    cellMask = xarray.DataArray(data=cellMask, dims=('nCells', 'nVertLevels'))
    edgeMask = xarray.DataArray(data=edgeMask, dims=('nEdges', 'nVertLevels'))

    plt.subplot(3, 3, 3)
    varName = 'layerThickness'
    var = ds[varName].isel(Time=0).where(cellMask)
    xarray.plot.hist(var, bins=100, log=True)
    plt.xlabel(varName)
    txt = '{}{:9.2e} {:9.2e} {}\n'.format(txt, var.min().values,
                                          var.max().values, varName)
    
    plt.subplot(3, 3, 4)
    varName = 'areaCell'
    var = ds[varName].where(cellMask)
    xarray.plot.hist(var, bins=100, log=True)
    plt.xlabel(varName)
    txt = '{}{:9.2e} {:9.2e} {}\n'.format(txt, var.min().values, 
                                          var.max().values, varName)
    plt.subplot(3, 3, 5)
    varName = 'widthCell'
    var = 2*np.sqrt(var/math.pi)/1000
    widthCell = np.asarray(var)[:, 0]
    xarray.plot.hist(var, bins=100, log=True)
    plt.xlabel(varName)
    txt = '{}{:9.2e} {:9.2e} {}\n'.format(txt, var.min().values, 
                                          var.max().values, varName)

    print(widthCell)
    print(widthCell.shape)
    fine = widthCell[widthCell < 12]
    coarse = widthCell[widthCell >= 12]
    ratio = coarse.shape[0] / fine.shape[0]
    txt = '{} num cells width >= 12km\n / num cells width < 12km\n     = {}\n'.format(txt, ratio)

    font = FontProperties()
    font.set_family('monospace')
    font.set_size(12)
    print(txt)
    plt.subplot(3, 3, 1)
    plt.text(0, 1, txt, verticalalignment='top', fontproperties=font)
    plt.axis('off')

    plt.tight_layout(pad=4.0)

    plt.savefig(args.output_file_name, bbox_inches='tight', pad_inches=0.1)


if __name__ == '__main__':
    # If called as a primary module, run main
    main()

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
