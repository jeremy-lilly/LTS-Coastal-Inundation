#!/usr/bin/env python

'''
plot global stats
August 2016, Mark Petersen, LANL
'''

from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np

outputDir = '.'
varList = ['normalVelocityMax']
varListMinMax = []
lt = '-:'

# open a the netCDF file for reading.
pngName = 'smalldt'
filePathName = './globalStats_smalldt.nc'
titleText = filePathName
print('Reading data from: ' + filePathName)
ncfile1 = Dataset(filePathName,'r') 
# read the data in variable named 'data'.
t1 = ncfile1.variables['daysSinceStartOfSim']
label1="dt = 10"

   
for var in varListMinMax:
   plt.clf()
   n=0
   dataMin = ncfile1.variables[var+'Min']
   dataMax = ncfile1.variables[var+'Max']
   dataAvg = ncfile1.variables[var+'Avg']
   plt.plot(t1, dataMin, lt[n], t1, dataAvg, lt[n], t1, dataMax, lt[n], label=label1)
   plt.xlabel('time, days')
   plt.ylabel(var)
   plt.title(titleText)
   plt.grid(True,which="both",ls="dotted")
   plt.xlim([0,0.05])
   plt.legend()
   plt.savefig(outputDir + '/' + pngName + '_' + var + '.png')
   print('Created plot: ' + outputDir + '/' + pngName + '_' + var + '.png')

for var in varList:
   plt.clf()
   n=0
   data = ncfile1.variables[var]
   plt.plot(t1, data, lt[n], label=label1)
   plt.xlabel('time, days')
   plt.ylabel(var)
   plt.title(titleText)
   plt.xlim([0,0.1])
   plt.legend()
   plt.grid(True,which="both",ls="dotted")
   plt.savefig(outputDir + '/' + pngName + '_' + var + '.png')
   print('Created plot: ' + outputDir + '/' + pngName + '_' + var + '.png')
  
ncfile1.close()

