#!/bin/bash
##parallel job
#SBATCH -J yt14W-loop
#SBATCH -D /mnt/home/jzhu1/ceph/1e14_cluster_halo_45_degree_wind              # setting work directory
#SBATCH --array=160-293%10 -N1 -c1 -o yt_analysis_loops_14W.o -p cca --qos=cca --constraint=opa
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

cd /mnt/home/jzhu1/ceph/1e14_cluster_halo_45_degree_wind

job_num=$(printf %04d $SLURM_ARRAY_TASK_ID)

data_dir='/mnt/home/stonnesen/ceph/jzhu1/1e14_cluster_halo_45_degree_wind'

echo "running analysis on DD$job_num/DD$job_num"


python ./SFR_2D_hist_local_Schmidt_single_output_for_parallel_job.py  ${data_dir}/DD$job_num/DD$job_num
##python ./global_quantity_loop_compre.py ${data_dir}/DD$job_num/DD$job_num
##python ./plot_fancy_density_slice.py ${data_dir}/DD$job_num/DD$job_num
