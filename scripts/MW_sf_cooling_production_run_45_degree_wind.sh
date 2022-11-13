#!/bin/bash
##parallel job
#SBATCH -J MW-cool
#SBATCH -D /mnt/home/jzhu1/ceph/MW_sf_cooling_multispecies_realistic_metals_45_degree_wind              # setting work directory
#SBATCH -N20 --ntasks-per-node=24 --exclusive -o MW-wind-tunnel-sf-cooling-isolated.o -p cca --qos=cca --constraint=skylake
#SBATCH --time=06-00:00            # Runtime in D-HH:MM
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
cd /mnt/home/jzhu1/ceph/MW_sf_cooling_multispecies_realistic_metals_45_degree_wind

srun -n 480 --mpi=pmi2 ./enzo_realistic_metals.exe  GalaxySimulation_low_mass_sf_with_cooling.enzo 
