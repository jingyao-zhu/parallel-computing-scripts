#!/bin/bash
##parallel job
#SBATCH -J test-cool
#SBATCH -D /mnt/home/jzhu1/ceph/wind-tunnel-rusty-grackle-test              # setting work directory
#SBATCH -N12 --ntasks-per-node=24 --exclusive -o wind-tunnel-sf-cooling-test.o -p preempt --qos=preempt --constraint=skylake
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
cd /mnt/home/jzhu1/ceph/wind-tunnel-rusty-grackle-test
##mpirun ./ GalaxySimulation.enzo
#srun -n 480 --mpi=pmi2 ./enzo_w_grackle.exe  GalaxySimulation_low_mass_sf_with_cooling_high_res.enzo
mpirun ./enzo_w_grackle_fixed_grid.exe  GalaxySimulation_grackle_debug.enzo 
