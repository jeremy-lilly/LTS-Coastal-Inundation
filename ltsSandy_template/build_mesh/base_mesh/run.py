#!/usr/bin/env python

# This script was generated from setup_testcases.py as part of a config file

import sys
import os
import shutil
import glob
import subprocess


dev_null = open('/dev/null', 'w')

# Run command is:
# ./build_base_mesh.py
subprocess.check_call(['./build_base_mesh.py'])
