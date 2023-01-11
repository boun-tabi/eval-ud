#!/bin/bash
#SBATCH --ntasks=2
#SBATCH --gpu-bind=closest
#SBATCH --gpus=1
#SBATCH --output=/clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/slurm/outputs/%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=furkanakkurt9285@gmail.com
#SBATCH --mem=40GB
#SBATCH -t 1-00:00

log_path=/clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/slurm/Logs.txt
date=$(date)
echo date: $date >> $log_path
echo job: $SLURM_JOB_ID >> $log_path
echo >> $log_path

env
python3 /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/steps-parser/src/train.py /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/lemma-only/configs/v2.8.json --resume /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/trained_models/boun_treebank_v2.8/lemma_only_baseline/0110_185404/model_best.pth
# python3 /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/steps-parser/src/train.py /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/lemma-only/configs/v2.8.json --resume /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/trained_models/boun_treebank_v2.8/lemma_only_baseline/0110_185358/model_best.pth # didn't work
# python3 /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/steps-parser/src/train.py /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/lemma-only/configs/v2.8.json --resume /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/trained_models/boun_treebank_v2.8/lemma_only_baseline/0110_185328/model_best.pth

RET=$?

exit $RET
