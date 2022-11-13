#!/bin/bash
##parallel job
#SBATCH -J nocool-mpi-test
#SBATCH -D /mnt/home/jzhu1/ceph/MW_nocool_test_MPI             # setting work directory
#SBATCH -N8 --ntasks-per-node=24 --exclusive -o RPS-nocooling-MW-test-MPI.o -p preempt --qos=preempt --constraint=skylake
#SBATCH --time=0-02:00            # Runtime in D-HH:MM
#SBATCH --mail-user=jz3289@columbia.edu
#SBATCH --mail-type=all

module --force purge
module load modules
module load slurm
module load gcc
module load openmpi
module load hdf5

export PATH=/mnt/home/jzhu1/build/yt-conda/bin:$PATH
export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/yt-conda/bin:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/yt-conda/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/grackle/lib:$LD_LIBRARY_PATH

echo $LD_LIBRARY_PATH
source /mnt/home/jzhu1/build/yt-conda/bin/activate
cd /mnt/home/jzhu1/ceph/MW_nocool_test_MPI
srun -n 192 --mpi=pmi2 ./enzo_nocool_multispecies_branch.exe -d GalaxySimulation_low_mass_no_cooling_high_res.enzo 
##mpirun ./enzo_wo_cooling.exe  GalaxySimulation_low_mass_no_cooling_high_res.enzo 
