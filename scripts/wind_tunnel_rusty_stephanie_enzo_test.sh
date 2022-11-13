#!/bin/bash
##parallel job
#SBATCH -J test-cool
#SBATCH -D /mnt/home/jzhu1/ceph/wind-tunnel-rusty-grid-test              # setting work directory
#SBATCH -N12 --ntasks-per-node=24 --exclusive -o wind-tunnel-sf-cooling-test.o -p preempt --qos=preempt --constraint=skylake
#SBATCH --time=0-05:00            # Runtime in D-HH:MM
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
cd /mnt/home/jzhu1/ceph/wind-tunnel-rusty-grid-test

mpirun ./enzo.exe  GalaxySimulation_grackle_debug.enzo
