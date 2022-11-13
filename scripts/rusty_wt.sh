#!/bin/bash
##parallel job
#SBATCH -N20 --ntasks-per-node=24 --exclusive -o RPSsfbb5lM8hmsdcdw.o -p cca --qos=cca --constraint=skylake
#SBATCH --mail-user=stonnesen@flatironinstitute.org
#SBATCH --mail-type=START,END,FAIL
module --force purge
module load modules
module load slurm
module load gcc
module load openmpi


export LD_LIBRARY_PATH=/mnt/home/stonnesen/grackle/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/mnt/home/stonnesen/yt-conda/pkgs/hdf5-1.8.18-1/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/mnt/home/stonnesen/yt-conda/lib:$LD_LIBRARY_PATH

echo $LD_LIBRARY_PATH
source /mnt/home/stonnesen/yt-conda/bin/activate
cd /mnt/ceph/users/stonnesen/Rory/RPSsfbb5lM8hmsdcdw
#mpirun ./enzo.exe GalaxySimulation.enzo
srun -n 360 --mpi=pmi2 ./enzo.exe -r DD0035/RPSsfbb5lM8hmsdcdw0035 #GalaxySimulation.enzo
