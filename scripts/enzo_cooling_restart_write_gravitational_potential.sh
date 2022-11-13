#!/bin/bash
##parallel job
#SBATCH -J io-gpot
#SBATCH -D /mnt/home/jzhu1/ceph/gravitational_potential_IO              # setting work directory
#SBATCH -N1 --ntasks-per-node=24 --exclusive -o 13W-pericenter-condition-write-gravitational-potential.o -p cca --qos=cca --constraint=opa
#SBATCH --time=0-01:00            # Runtime in D-HH:MM
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
cd /mnt/home/jzhu1/ceph/gravitational_potential_IO

srun -n 24 --mpi=pmi2 ./enzo_sf_test_h5.exe -r -g DD0253/DD0253
