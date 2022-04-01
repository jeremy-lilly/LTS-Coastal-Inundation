#!/usr/bin/env python

# This script was generated from setup_testcases.py as part of a config file

import sys
import os
import shutil
import glob
import subprocess


dev_null = open('/dev/null', 'w')

# Run command is:
# ./cull_mesh.py --with_critical_passages
subprocess.check_call(['./cull_mesh.py', '--with_critical_passages'])

# Run command is:
# inject_bathymetry culled_mesh.nc
subprocess.check_call(['inject_bathymetry', 'culled_mesh.nc'])

# Run command is:
# paraview_vtk_field_extractor.py --ignore_time -l -d maxEdges=0 -v allOnCells
# -f culled_mesh.nc -o culled_mesh_vtk
subprocess.check_call(['paraview_vtk_field_extractor.py', '--ignore_time',
                       '-l', '-d', 'maxEdges=0', '-v', 'allOnCells', '-f',
                       'culled_mesh.nc', '-o', 'culled_mesh_vtk'])

# Run command is:
# ./label_mesh_lts.py
subprocess.check_call(['./label_mesh_lts.py'])

