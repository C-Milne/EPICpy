#!/bin/bash

#SBATCH --job-name=Profiler
#SBATCH --mail-user=u34cm18@abdn.ac.uk
#SBATCH --mail-type=ALL
#SBATCH -o slurm.%j.out
#SBATCH -e slurm.%j.err
#SBATCH --ntasks=1
#SBATCH --time=1:00:00
#SBATCH --partition=compute

date
hostname
module load python-3.9.1

python ./runner-cprofiler.py
