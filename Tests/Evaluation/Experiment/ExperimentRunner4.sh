#!/bin/bash

#SBATCH --job-name=VerifyRunner4
#SBATCH --mail-user=u34cm18@abdn.ac.uk
#SBATCH --mail-type=ALL
#SBATCH -o slurms/slurm.%j.out
#SBATCH -e slurms/slurm.%j.err
#SBATCH --ntasks=1
#SBATCH --mem 24G
#SBATCH --time=170:00:00
#SBATCH --partition=compute

date
hostname
module load python-3.9.1

python ./ER4.py
