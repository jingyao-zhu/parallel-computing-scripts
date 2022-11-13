#!/bin/bash
##parallel job
#SBATCH -J low-pres-wind
#SBATCH -D /mnt/home/jzhu1/ceph/MW_sf_cooling_45degree_wind              # setting work directory
#SBATCH -N18 --ntasks-per-node=24 --exclusive -o isolated-galaxy-1e12halo-sf-cooling-restart2-with-wind-250Myr.o -p preempt --qos=preempt --constraint=skylake
#SBATCH --time=0-09:00            # Runtime in D-HH:MM
#SBATCH --mail-user=jz3289@columbia.edu
#SBATCH --mail-type=all

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
cd /mnt/home/jzhu1/ceph/MW_sf_cooling_45degree_wind

srun -n 480 --mpi=pmi2 ./enzo_multispecies.exe -r DD0026/DD0026
