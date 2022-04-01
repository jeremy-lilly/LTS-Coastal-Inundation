#!/usr/bin/env python


import argparse as ap
import subprocess as sp
import numpy as np
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


def main(solution):

    # input variables (get these via argparse later)
    numProcs = 144
    maxDT = 18
    inputMesh = 'input.nc'


    ### Runs

    setConfigs('namelist.ocean', {'config_dt': str(maxDT)})
    shCommand = 'srun -n ' + str(numProcs) + ' ocean_model -n namelist.ocean -s streams.ocean'
    print(shCommand)
    sp.call(shCommand.split())

    shCommand = 'mv output.nc output1.nc'
    print(shCommand)
    sp.call(shCommand.split())
    
    
    setConfigs('namelist.ocean', {'config_dt': str(maxDT/2)})
    shCommand = 'srun -n ' + str(numProcs) + ' ocean_model -n namelist.ocean -s streams.ocean'
    print(shCommand)
    sp.call(shCommand.split())

    shCommand = 'mv output.nc output2.nc'
    print(shCommand)
    sp.call(shCommand.split())

    
    setConfigs('namelist.ocean', {'config_dt': str(maxDT/4)})
    shCommand = 'srun -n ' + str(numProcs) + ' ocean_model -n namelist.ocean -s streams.ocean'
    print(shCommand)
    sp.call(shCommand.split())

    shCommand = 'mv output.nc output3.nc'
    print(shCommand)
    sp.call(shCommand.split())


    ### Rate calculations

    ncFile1 = Dataset('output1.nc', 'r') 
    ncFile2 = Dataset('output2.nc', 'r') 
    ncFile3 = Dataset('output3.nc', 'r')

    if solution:
        solFile = Dataset(solution, 'r')
        ltSol = solFile.variables['layerThickness'][-1, :, :]
        nvSol = solFile.variables['normalVelocity'][-1, :, :]
        
        # out1 compared to soln
        var = ncFile1.variables['layerThickness'][-1, :, :]
        dif = abs(var - ltSol)
        numl2 = dif**2
        ltErr1 = np.sqrt(np.sum(numl2[:]))
        print('\n--rms err in layerThickness (run 1 vs ref sol) = ' + str(ltErr1 / np.sqrt(numl2.size)))
        print('--Max err in layerThickness (run 1 vs ref sol) = ' + str(np.max(dif)))

        var = ncFile1.variables['normalVelocity'][-1, :, :]
        dif = abs(var - nvSol)
        numl2 = dif**2
        nvErr1 = np.sqrt(np.sum(numl2[:]))
        print('--rms err in normalVelocity (run 1 vs ref sol) = ' + str(nvErr1 / np.sqrt(numl2.size)))
        print('--Max err in normalVelocity (run 1 vs ref sol) = ' + str(np.max(dif)))

        
        # out2 compared to soln
        var = ncFile2.variables['layerThickness'][-1, :, :]
        dif = abs(var - ltSol)
        numl2 = dif**2
        ltErr2 = np.sqrt(np.sum(numl2[:]))
        print('\n--rms err in layerThickness (run 2 vs ref sol) = ' + str(ltErr2 / np.sqrt(numl2.size)))
        print('--Max err in layerThickness (run 2 vs ref sol) = ' + str(np.max(dif)))

        var = ncFile2.variables['normalVelocity'][-1, :, :]
        dif = abs(var - nvSol)
        numl2 = dif**2
        nvErr2 = np.sqrt(np.sum(numl2[:]))
        print('--rms err in normalVelocity (run 2 vs ref sol) = ' + str(nvErr2 / np.sqrt(numl2.size)))
        print('--Max err in normalVelocity (run 2 vs ref sol) = ' + str(np.max(dif)))

        
        # out3 compared to soln
        var = ncFile3.variables['layerThickness'][-1, :, :]
        dif = abs(var - ltSol)
        numl2 = dif**2
        ltErr3 = np.sqrt(np.sum(numl2[:]))
        print('\n--rms err in layerThickness (run 3 vs ref sol) = ' + str(ltErr3 / np.sqrt(numl2.size)))
        print('--Max err in layerThickness (run 3 vs ref sol) = ' + str(np.max(dif)))

        var = ncFile3.variables['normalVelocity'][-1, :, :]
        dif = abs(var - nvSol)
        numl2 = dif**2
        nvErr3 = np.sqrt(np.sum(numl2[:]))
        print('--rms err in normalVelocity (run 3 vs ref sol) = ' + str(nvErr3 / np.sqrt(numl2.size)))
        print('--Max err in normalVelocity (run 3 vs ref sol) = ' + str(np.max(dif)))
        
        
        print('\n---Convergence rate for layerThickness (err1/err2) = ' + str(log(ltErr1/ltErr2, 2)))
        print('---Convergence rate for normalVelocity (err1/err2) = ' + str(log(nvErr1/nvErr2, 2)))

        print('\n---Convergence rate for layerThickness (err2/err3) = ' + str(log(ltErr2/ltErr3, 2)))
        print('---Convergence rate for normalVelocity (err2/err3) = ' + str(log(nvErr2/nvErr3, 2)))

        
        solFile.close()
    else:
        # out1 compared to out2
        var = ncFile1.variables['layerThickness'][-1, :, :]
        sol = ncFile2.variables['layerThickness'][-1, :, :]
        dif = abs(var - sol)
        numl2 = dif**2
        ltErr1 = np.sqrt(np.sum(numl2[:]))
        print('\n--rms err in layerThickness (run 1 vs run 2) = ' + str(ltErr1 / np.sqrt(numl2.size)))
        print('--Max err in layerThickness (run 1 vs run 2) = ' + str(np.max(dif)))
        print('--max normalized err in layerThickness (run 1 vs run 2) = ' + str( np.max( abs( var - sol ) / sol ) ))
        
        var = ncFile1.variables['normalVelocity'][-1, :, :]
        sol = ncFile2.variables['normalVelocity'][-1, :, :]
        dif = abs(var - sol)
        numl2 = dif**2
        nvErr1 = np.sqrt(np.sum(numl2[:]))
        print('--rms err in normalVelocity (run 1 vs run 2) = ' + str(nvErr1 / np.sqrt(numl2.size)))
        print('--Max err in normalVelocity (run 1 vs run 2) = ' + str(np.max(dif)))
        print('--max normalized err in normalVelocity (run 1 vs run 2) = ' + str( np.max( abs( var - sol ) / sol ) ))

        
        # out2 compared to out3
        var = ncFile2.variables['layerThickness'][-1, :, :]
        sol = ncFile3.variables['layerThickness'][-1, :, :]
        dif = abs(var - sol)
        numl2 = dif**2
        ltErr2 = np.sqrt(np.sum(numl2[:]))
        print('\n--rms err in normalVelocity (run 2 vs run 3) = ' + str(ltErr2 / np.sqrt(numl2.size)))
        print('--Max err in layerThickness (run 2 vs run 3) = ' + str(np.max(dif)))
        print('--max normalized err in layerThickness (run 2 vs run 3) = ' + str( np.max( abs( var - sol ) / sol ) ))
        
        var = ncFile2.variables['normalVelocity'][-1, :, :]
        sol = ncFile3.variables['normalVelocity'][-1, :, :]
        dif = abs(var - sol)
        numl2 = dif**2
        nvErr2 = np.sqrt(np.sum(numl2[:]))
        print('--rms err in normalVelocity (run 2 vs run 3) = ' + str(nvErr2 / np.sqrt(numl2.size)))
        print('--Max err in normalVelocity (run 2 vs run 3) = ' + str(np.max(dif)))
        print('--max normalized err in normalVelocity (run 2 vs run 3) = ' + str( np.max( abs( var - sol ) / sol ) ))
        
        
        print('\n---Convergence rate for layerThickness = ' + str(log(ltErr1/ltErr2, 2)))
        print('---Convergence rate for normalVelocity = ' + str(log(nvErr1/nvErr2, 2)))
    # END if

    
    ncFile1.close()
    ncFile2.close()
    ncFile3.close()


# END main()


if __name__ == '__main__':
    # if called as primary module, run main
    
    parser = ap.ArgumentParser(description='Python script to test convergence rate in time.')

    parser.add_argument('-s', '--solution', dest='solution', 
                        help='NetCDF file containing a reference solution.')

    args = parser.parse_args()


    main(args.solution)

