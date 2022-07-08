#!/usr/bin/env python


import argparse as ap
import subprocess as sp
import numpy as np
import pickle as pkl
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from math import log


def setConfigs(fileName, configDict):
    
    with open(fileName, 'r') as iFile:
        oldTxt = iFile.read()
        newTxt = ''
        for line in oldTxt.split('\n'):
            lineChanged = False
            words = line.split()
            for key in configDict.keys():
                if key in words:
                    words[-1] = "'" + configDict[key] + "'"
                    newTxt += '    ' + ' '.join(words) + '\n'
                    lineChanged = True
                # END if
            # END for
            if not lineChanged:
                newTxt += line + '\n'
            # END if
        # END for
    # END with

    with open('namelist.ocean', 'w') as oFile:
        oFile.write(newTxt)

# END setConfigs()


def rmse(sol1, sol2):
    diff = abs(sol1 - sol2)
    err = np.sqrt(np.mean(diff**2))
    #err = np.sqrt(np.sum(diff**2))
    
    return err
# END rmse()


def main(solution, in_pickle, out_pickle, plot_name, method):

    if method == 'RK4':
        perfectRate = 4
    elif method == 'LTS3' or method == 'SSPRK3':
        perfectRate = 3
    else:
        print('bad method')
        quit()

    scaleFactor = 10**(-9 - perfectRate)

    if not in_pickle:

        # input variables (maybe get these via argparse later)
        numProcs = 36
        dts = [12, 8, 6]
        #dts = [36, 18, 12]
        #dts = [36, 24, 20, 16]
        
        layerThicknesses = []
        normalVelocities = []

        layerThicknessErrs = []
        normalVelocityErrs = []

        sol = Dataset(solution, 'r')
        layerThicknessSol = sol.variables['layerThickness'][-1, :, :]
        normalVelocitySol = sol.variables['normalVelocity'][-1, :, :]
        sol.close()

        for dt in dts:
            setConfigs('namelist.ocean', {'config_dt': str(dt)})
            print('---dt = ' + str(dt))
            shCommand = 'srun -n ' + str(numProcs) + ' ocean_model_ramp1 -n namelist.ocean -s streams.ocean'
            print(shCommand)
            sp.call(shCommand.split())

            out = Dataset('output.nc', 'r')
            lt = out.variables['layerThickness'][-1, :, :]
            nv = out.variables['normalVelocity'][-1, :, :]
            out.close()
            
            
            layerThicknesses.append(lt)
            normalVelocities.append(nv)

            layerThicknessErrs.append(rmse(layerThicknessSol, lt))
            normalVelocityErrs.append(rmse(normalVelocitySol, nv))

        # END for

        pickleDict = {'layerThicknessSol': layerThicknessSol,
                      'normalVelocitySol': normalVelocitySol,
                      'dts': dts,
                      'layerThicknesses': layerThicknesses,
                      'normalVelocities': normalVelocities,
                      'layerThicknessErrs': layerThicknessErrs,
                      'normalVelocityErrs': normalVelocityErrs}

        with open(out_pickle, 'wb') as oFile:
            pkl.dump(pickleDict, oFile)
        # END with
    
    
    else:
        
        with open(in_pickle, 'rb') as iFile:
            pickleDict = pkl.load(iFile)
        # END with
        
        dts = pickleDict['dts']
        layerThicknessErrs = pickleDict['layerThicknessErrs']
        normalVelocityErrs = pickleDict['normalVelocityErrs']

        ############
        layerThicknesses = pickleDict['layerThicknesses']
        normalVelocities = pickleDict['normalVelocities']
        layerThicknessSol = pickleDict['layerThicknessSol']
        normalVelocitySol = pickleDict['normalVelocitySol']

        for i, dt in enumerate(dts):
            print('---dt = ' + str(dt))
            print('--err in layerThickness = ' + str(layerThicknessErrs[i]) )
            print('--err in normalVelocity = ' + str(normalVelocityErrs[i]) )
            print('--max normalized err in layerThickness = ' + str( np.max( abs( layerThicknesses[i] - layerThicknessSol ) / layerThicknessSol ) ))
            print('--max normalized err in normalVelocity = ' + str( np.max( abs( normalVelocities[i] - normalVelocitySol ) / normalVelocitySol ) ))
            print('--avg normalized err in layerThickness = ' + str( np.mean( abs( layerThicknesses[i] - layerThicknessSol ) / layerThicknessSol ) ))
            print('--avg normalized err in normalVelocity = ' + str( np.mean( abs( normalVelocities[i] - normalVelocitySol ) / normalVelocitySol ) ))
    
    # END if

    fig, ax = plt.subplots(1, 1)

    ltFitCoefs = np.polyfit(np.log10(dts), np.log10(layerThicknessErrs), 1)
    #ltFitCoefs = np.polyfit(dts, layerThicknessErrs, 1)
    ltFit = ltFitCoefs[0]*np.log10(dts) + ltFitCoefs[1]
    nvFitCoefs = np.polyfit(np.log10(dts), np.log10(normalVelocityErrs), 1)
    #nvFitCoefs = np.polyfit(dts, normalVelocityErrs, 1)
    nvFit = nvFitCoefs[0]*np.log10(dts) + nvFitCoefs[1]
    perfect = scaleFactor * np.asarray(dts)**perfectRate

    print('----best fit rate for layerThickness = ' + str(ltFitCoefs[0]))
    print('----best fit rate for normalVelocity = ' + str(nvFitCoefs[0]))
    
    ax.loglog(dts, layerThicknessErrs, '--o', color='tab:blue', label='layer thickness, order = {:.2f}'.format(ltFitCoefs[0]))
    #ax.loglog(dts, 10**ltFit, '-', color='tab:blue')
    
    ax.loglog(dts, normalVelocityErrs, '--o', color='tab:orange', label='normal velocity, order = {:.2f}'.format(nvFitCoefs[0]))
    #ax.loglog(dts, 10**nvFit, '-', color='tab:orange')
    
    ax.loglog(dts, perfect, 'k-', label='order {}'.format(perfectRate))
    
    ax.set(xlabel='dt (s)',
           ylabel='RMS Error',
           title='Convergence in time for ' + method)
    #ax.set_xlim(dts[-1] - 1, dts[0] + 1)
    #ax.set_ylim(10**(-10), 10**(-7))
    ax.set_xticks([12])
    ax.legend()

    plt.savefig(plot_name)

    
# END main()


if __name__ == '__main__':
    # if called as primary module, run main
    
    parser = ap.ArgumentParser(description='Python script to test convergence rate in time.')

    parser.add_argument('-s', '--solution', dest='solution', 
                        help='NetCDF file containing a reference solution.')
    
    parser.add_argument('-i', '--in-pickle', dest='in_pickle', 
                        help='Pickled data from a previous run of this script.')
    
    parser.add_argument('-o', '--out-pickle', dest='out_pickle',
                        default='convergence_data.pkl',
                        help='Name for output pickle file.')
    
    parser.add_argument('-p', '--plot-name', dest='plot_name',
                        default='convergence_plot.png',
                        help='Name for output plot png.')
    
    parser.add_argument('-m', '--method', dest='method',
                        default='RK4',
                        help='Name of time-stepping method.')

    args = parser.parse_args()


    main(args.solution, args.in_pickle, args.out_pickle, args.plot_name, args.method)

