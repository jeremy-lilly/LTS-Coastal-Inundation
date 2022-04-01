#!/usr/bin/env python

# This script was generated from setup_testcases.py as part of a config file

import sys
import os
import shutil
import glob
import subprocess


dev_null = open('/dev/null', 'w')

# Run command is:
# python interpolate_time_varying_forcing.py
subprocess.check_call(['python', 'interpolate_time_varying_forcing.py'])

# Run command is:
# python create_pointstats_file.py --mesh_file mesh.nc --station_files
# USGS_stations.txt --station_files NOAA-COOPS_stations.txt
subprocess.check_call(['python', 'create_pointstats_file.py', '--mesh_file',
                       'mesh.nc', '--station_files', 'USGS_stations.txt',
                       '--station_files', 'NOAA-COOPS_stations.txt'])
print("\n")
print("     *****************************")
print("     ** Starting model run step **")
print("     *****************************")
print("\n")
os.environ['OMP_NUM_THREADS'] = '1'

# Run command is:
# mpirun -n 1 ./ocean_model -n namelist.ocean -s streams.ocean
subprocess.check_call(['mpirun', '-n', '1', './ocean_model', '-n',
                       'namelist.ocean', '-s', 'streams.ocean'])
print("\n")
print("     *****************************")
print("     ** Finished model run step **")
print("     *****************************")
print("\n")

# Run command is:
# python interpolate_rinv_edge.py
subprocess.check_call(['python', 'interpolate_rinv_edge.py'])

