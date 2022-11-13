#!/bin/bash
##parallel job
#SBATCH -J yt12W-loop
#SBATCH -D /mnt/home/jzhu1/ceph/MW_sf_cooling_multispecies_realistic_metals_45_degree_wind              # setting work directory
#SBATCH --array=000-144%10 -N1 -c1 -o yt_analysis_loop_12W.o -p cca --qos=cca --constraint=opa
#SBATCH --time=00-10:00            # Runtime in D-HH:MM
#SBATCH --mail-user=jz3289@columbia.edu
#SBATCH --mail-type=all

module --force purge
module load modules
module load slurm
module load gcc
module load openmpi
module load openmpi-opa
module load hdf5

export LD_LIBRARY_PATH=/mnt/home/jzhu1/build/yt-conda/bin:$LD_LIBRARY_PATH
source /mnt/home/jzhu1/build/yt-conda/bin/activate

cd /mnt/home/jzhu1/ceph/MW_sf_cooling_multispecies_realistic_metals_45_degree_wind

job_num=$(printf %04d $SLURM_ARRAY_TASK_ID)

echo "running analysis on DD$job_num/DD$job_num"


python ./SFR_2D_hist_local_Schmidt_single_output_for_parallel_job.py DD$job_num/DD$job_num
##python ./plot_fancy_density_slice.py DD$job_num/DD$job_num
##python ./global_quantity_loop_compre.py DD$job_num/DD$job_num
##python ./phaseplot_yt_loops.py DD$job_num/DD$job_num
