#!/bin/bash
##parallel job
#SBATCH -J grac-cool
#SBATCH -D  /mnt/home/jzhu1/ceph/enzo_cooling_tests/CoolingTest_Grackle             # setting work directory
#SBATCH -N4 --ntasks-per-node=24 --exclusive -o test-one-zone-cooling-grackle.o -p cca --qos=cca --constraint=skylake
#SBATCH --time=0-04:00            # Runtime in D-HH:MM
#SBATCH --mail-user=jz3289@columbia.edu
#SBATCH --mail-type=all

module --force purge
module load modules
module load slurm
module load gcc
module load openmpi

export PATH=/mnt/home/jzhu1/build/yt-conda/bin:$PATH
export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/yt-conda/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/grackle/lib:$LD_LIBRARY_PATH

echo $LD_LIBRARY_PATH
##source /mnt/home/jzhu1/build/yt-conda/bin/activate
cd /mnt/home/jzhu1/ceph/enzo_cooling_tests/CoolingTest_Grackle
##mpirun ./ GalaxySimulation.enzo
##srun -n 192 --mpi=pmi2 
mpirun ./enzo_w_grackle.exe CoolingTest_Grackle.enzo 
