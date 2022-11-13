#!/bin/bash
##parallel job
#SBATCH -J iso-gala-rst4
#SBATCH -D /mnt/home/jzhu1/ceph/MW_sf_cooling_multispecies_realistic_metals_isolated              # setting work directory
#SBATCH -N12 --ntasks-per-node=24 --exclusive -o isolated-galaxy-1e12halo-sf-cooling-restart4.o -p preempt --qos=preempt --constraint=skylake
#SBATCH --time=0-02:00            # Runtime in D-HH:MM
#SBATCH --mail-user=jz3289@columbia.edu
#SBATCH --mail-type=all

module --force purge
module load modules
module load slurm
module load gcc
module load openmpi
module load hdf5

#export LD_LIBRARY_PATH=/mnt/home/stonnesen/grackle/lib:$LD_LIBRARY_PATH
#export LD_LIBRARY_PATH=/mnt/home/stonnesen/yt-conda/pkgs/hdf5-1.8.18-1/lib:$LD_LIBRARY_PATH
#export LD_LIBRARY_PATH=/mnt/home/stonnesen/yt-conda/lib:$LD_LIBRARY_PATH

export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/grackle/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/yt-conda/lib:$LD_LIBRARY_PATH
echo $LD_LIBRARY_PATH
#source /mnt/home/stonnesen/yt-conda/bin/activate
cd /mnt/home/jzhu1/ceph/MW_sf_cooling_multispecies_realistic_metals_isolated

#mpirun ./enzo_realistic_metals_jzhu_modules.exe -r DD0040/DD0040
srun -n 288 --mpi=pmi2 ./enzo_realistic_metals_jzhu_modules.exe -r DD0042/DD0042
#srun -n 480 --mpi=pmi2 ./enzo_realistic_metals.exe -r DD0040/DD0040
