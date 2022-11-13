#!/bin/bash
##parallel job
#SBATCH -J 12W-peri
#SBATCH -D /mnt/home/jzhu1/ceph/MW_sf_cooling_multispecies_realistic_metals_45_degree_wind              # setting work directory
#SBATCH -N12 --ntasks-per-node=24 --exclusive -o 45degree-wind-1e12halo-sf-cooling-restart15-attached-flat-pericenter.o -p cca --qos=cca --constraint=opa
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
cd /mnt/home/jzhu1/ceph/MW_sf_cooling_multispecies_realistic_metals_45_degree_wind

srun -n 288 --mpi=pmi2 ./enzo_sf_test_h5.exe -r DD0113/DD0113
