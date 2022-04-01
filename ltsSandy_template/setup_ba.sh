#!/bin/bash

#SBATCH --nodes=1
#SBATCH --mail-user=lillyj@oregonstate.edu
#SBATCH --mail-type=ALL
#SBATCH --account=t22_ocean_time_step
#SBATCH --qos=long
#SBATCH --time=48:00:00

date >> time.txt
module use /usr/projects/climate/SHARED_CLIMATE/modulefiles/spack-lmod/linux-rhel7-x86_64; module load gcc/6.4.0; module load openmpi/2.1.2; module load cmake/3.12.1; module load mkl; module load openmpi/2.1.2-bheb4xe/gcc/6.4.0/netcdf/4.4.1.1-zei2j6r ;module load openmpi/2.1.2-bheb4xe/gcc/6.4.0/netcdf-fortran/4.4.4-v6vwmxs; module load openmpi/2.1.2-bheb4xe/gcc/6.4.0/parallel-netcdf/1.8.0-2qwcdbn; module load openmpi/2.1.2-bheb4xe/gcc/6.4.0/pio/1.10.0-ljj73au; module unload python; source /usr/projects/climate/SHARED_CLIMATE/anaconda_envs/load_latest_compass.sh;
cd build_mesh
./run.py
cd ../sandy/init
./run.py
date >> time.txt

