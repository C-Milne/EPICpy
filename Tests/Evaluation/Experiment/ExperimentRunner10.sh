#!/bin/bash

#SBATCH --job-name=ExperimentRunner10
#SBATCH --mail-user=u34cm18@abdn.ac.uk
#SBATCH --mail-type=ALL
#SBATCH -o slurm.%j.out
#SBATCH -e slurm.%j.err
#SBATCH --ntasks=1
#SBATCH --time=48:00:00
#SBATCH --partition=compute

date
hostname
module load python-3.9.1

python ./ER10.py
