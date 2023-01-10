#!/bin/bash
#SBATCH --ntasks=2
#SBATCH --gpu-bind=closest
#SBATCH --gpus=1
#SBATCH --output=/clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/slurm/outputs/%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=furkanakkurt9285@gmail.com
#SBATCH --mem=40GB
#SBATCH -t 0-5:00

log_path=/clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/slurm/Logs.txt
date=$(date)
echo date: $date >> $log_path
echo train-type: $1 >> $log_path
echo treebank: $2 >> $log_path
echo job: $SLURM_JOB_ID >> $log_path
echo >> $log_path

env
python3 /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/configs/main.py --train-type $1 --treebank $2
python3 /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/steps-parser/src/train.py /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/configs/$SLURM_JOB_ID.json

RET=$?

exit $RET
