#!/bin/bash
#SBATCH --ntasks=2
#SBATCH --gpu-bind=closest
#SBATCH --gpus=1
#SBATCH --output=/clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/slurm/outputs/%j-steps-parser_dep_parsing_v2.8.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=furkanakkurt9285@gmail.com
#SBATCH --mem=40gb
#SBATCH -t 0-5:00

env
python3 /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/steps-parser/src/train.py /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/dep-parsing/configs/dep_parsing_v2.8.json

RET=$?

exit $RET
