#!/bin/bash
#SBATCH --ntasks=2
#SBATCH --gpu-bind=closest
#SBATCH --gpus=1
#SBATCH --output=/clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/slurm/outputs/%j-steps-parser_lemma_only_baseline_v2.11-no-epoch-limit.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=furkanakkurt9285@gmail.com
#SBATCH --mem=20GB
#SBATCH -t 2-00:00

env
python3 /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/steps-parser/src/train.py /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/lemma-only/configs/lemma_only_baseline_v2.11-no-epoch-limit.json

RET=$?

exit $RET
