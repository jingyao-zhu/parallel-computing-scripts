#!/bin/bash
##parallel job
#SBATCH -J 1e13-peri3
#SBATCH -D /mnt/home/jzhu1/ceph/1e13_group_halo_45_degree_wind              # setting work directory
#SBATCH -N20 --ntasks-per-node=24 --exclusive -o 45degree-wind-1e13halo-sf-cooling-stacked-ICM-profile-restart9-pericenter-wind3.o -p cca --qos=cca --constraint=opa
#SBATCH --time=01-00:00            # Runtime in D-HH:MM
#SBATCH --mail-user=jz3289@columbia.edu
#SBATCH --mail-type=all

module --force purge
module load modules
module load slurm
module load gcc
module load openmpi
module load openmpi-opa
module load hdf5

##export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/yt-conda/bin:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/grackle/lib:$LD_LIBRARY_PATH
##export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/yt-conda/lib:$LD_LIBRARY_PATH
##source /mnt/home/jzhu1/build/yt-conda/bin/activate

echo $LD_LIBRARY_PATH
cd /mnt/home/jzhu1/ceph/1e13_group_halo_45_degree_wind

srun -n 480 --mpi=pmi2 ./enzo_sf_test_h5.exe -r DD0259/DD0259
