#!/bin/bash
##parallel job
#SBATCH -J iso-gala-rst15
#SBATCH -D /mnt/home/jzhu1/ceph/MW_sf_cooling_multispecies_realistic_metals_isolated              # setting work directory
#SBATCH -N12 --ntasks-per-node=24 --exclusive -o isolated-galaxy-1e12halo-sf-cooling-restart15.o -p cca --qos=cca --constraint=opa
#SBATCH --time=7-00:00            # Runtime in D-HH:MM
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
cd /mnt/home/jzhu1/ceph/MW_sf_cooling_multispecies_realistic_metals_isolated

srun -n 288 --mpi=pmi2 ./enzo_sf_test_h5.exe -r DD0263/DD0263
