#!/bin/bash

#SBATCH --job-name=ExperimentRunner2
#SBATCH --mail-user=u34cm18@abdn.ac.uk
#SBATCH --mail-type=ALL
#SBATCH -e slurm.%j.err
#SBATCH --ntasks=1
#SBATCH --time=48:00:00
#SBATCH --partition=compute
SBATCH --mem 8G

date
hostname
module load python-3.9.1

python ./ER2.py
