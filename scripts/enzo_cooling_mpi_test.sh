#!/bin/bash
##parallel job
#SBATCH -J enzo-sf-mpi-test
#SBATCH -D /mnt/home/jzhu1/ceph/MW_sf_cooling_MPI_test              # setting work directory
#SBATCH -N12 --ntasks-per-node=24 --exclusive -o enzo-sf-cool-mpi-debug-test.o -p preempt --qos=preempt --constraint=skylake
#SBATCH --time=0-02:00            # Runtime in D-HH:MM
#SBATCH --mail-user=jz3289@columbia.edu
#SBATCH --mail-type=all

module --force purge
module load modules
module load slurm
module load gcc
module load openmpi
##module load hdf5

export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/grackle/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/yt-conda/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/yt-conda/bin:$LD_LIBRARY_PATH
source /mnt/home/jzhu1/build/yt-conda/bin/activate
echo $LD_LIBRARY_PATH

cd /mnt/home/jzhu1/ceph/MW_sf_cooling_MPI_test

srun -n 288 --mpi=pmi2 ./enzo_test_star_maker_rand.exe -d GalaxySimulation_low_mass_sf_with_cooling.enzo
