#!/bin/bash
##parallel job
#SBATCH -J test-perf
#SBATCH -D /mnt/home/jzhu1/ceph/MW_sf_cooling_multispecies_realistic_metals_45_degree_wind/test_euler_performance              # setting work directory
#SBATCH -N20 --ntasks-per-node=24 --exclusive -o 45degree-wind-1e12halo-sf-cooling-test-performance.o -p preempt --qos=preempt --constraint=opa
#SBATCH --time=00-24:00            # Runtime in D-HH:MM
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
cd /mnt/home/jzhu1/ceph/MW_sf_cooling_multispecies_realistic_metals_45_degree_wind/test_euler_performance

srun -n 480 --mpi=pmi2 ./enzo_module_h5_test_euler_smallrho_energy_floor.exe -r DD0053/DD0053
