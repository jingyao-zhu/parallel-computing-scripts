#!/bin/bash
##parallel job
#SBATCH -J Massive-SF
#SBATCH -D  /mnt/home/jzhu1/ceph/Massive-halo-sf-with-cooling-test             # setting work directory
#SBATCH -N20 --ntasks-per-node=24 --exclusive -o RPS-sf-with-cooling-massive-host-test-omp.o -p cca --qos=cca --constraint=skylake
#SBATCH --time=0-12:00            # Runtime in D-HH:MM
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
cd /mnt/home/jzhu1/ceph/Massive-halo-sf-with-cooling-test
##mpirun ./ GalaxySimulation.enzo
#srun -n 480 --mpi=pmi2 ./enzo_w_grackle.exe  GalaxySimulation_low_mass_sf_with_cooling_high_res.enzo
#mpirun ./enzo_w_grackle.exe GalaxySimulation_low_mass_sf_with_cooling_high_res.enzo 
mpirun ./enzo_w_grackle_revised_multispecies_omp.exe  GalaxySimulation_low_mass_sf_with_cooling_high_res.enzo 
