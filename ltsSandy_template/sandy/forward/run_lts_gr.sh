#!/bin/bash

#SBATCH --nodes=4
#SBATCH --mail-user=lillyj@oregonstate.edu
#SBATCH --mail-type=ALL
#SBATCH --account=t22_ocean_time_step
#SBATCH --time=12:00:00

date >> time.txt
module purge; module load git; module use /usr/projects/climate/SHARED_CLIMATE/modulefiles/all/; module unload python; source /usr/projects/climate/SHARED_CLIMATE/anaconda_envs/load_latest_compass.sh; module load gcc/5.3.0 openmpi/1.10.5 netcdf/4.4.1 parallel-netcdf/1.5.0 pio/1.7.2;
./run_lts.py
date >> time.txt
