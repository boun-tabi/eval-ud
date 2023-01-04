#!/bin/bash
#SBATCH --ntasks=2
#SBATCH --gpu-bind=closest
#SBATCH --gpus=1
#SBATCH --output=/clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/slurm/outputs/%j-steps-parser_pos_only_baseline_v2.8.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=furkanakkurt9285@gmail.com
#SBATCH --mem=40gb
#SBATCH -t 0-5:00

env
python3 /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/steps-parser/src/train.py /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/trains/pos-only/configs/pos_only_baseline_v2.8.json --resume /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/trained_models/boun_treebank_v2.8/pos_only_baseline/1210_112647/checkpoint-epoch40.pth


RET=$?

exit $RET
