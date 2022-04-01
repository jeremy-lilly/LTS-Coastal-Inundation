#!/usr/bin/env python

# This script was generated from setup_testcases.py as part of a config file

import sys
import os
import shutil
import glob
import subprocess


dev_null = open('/dev/null', 'w')

numProcs = 144

# Run command is:
# ./generate_graph_info_part_lts.py -l numBlocks
subprocess.check_call(['./generate_graph_info_part_lts.py', '-b', str(numProcs*3)])
print("\n")
print("     *****************************")
print("     ** Starting model run step **")
print("     *****************************")
print("\n")
os.environ['OMP_NUM_THREADS'] = '1'

# Run command is:
# mpirun -n 144 ./ocean_model -n namelist.ocean.lts -s streams.ocean
subprocess.check_call(['mpirun', '-n', str(numProcs), './ocean_model', '-n',
                       'namelist.ocean.lts', '-s', 'streams.ocean'])
print("\n")
print("     *****************************")
print("     ** Finished model run step **")
print("     *****************************")
print("\n")
