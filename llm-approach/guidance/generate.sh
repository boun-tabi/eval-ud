#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --gpu-bind=closest
#SBATCH --gpus=1
#SBATCH --output=/clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/llm-approach/guidance/outs/%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=furkanakkurt9285@gmail.com
#SBATCH --mem=40GB
#SBATCH -t 1-00:00

echo Start date and time: $(date)
echo Environment:
env
echo
/clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/.venv/bin/python3 /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/llm-approach/guidance/generate.py -d /clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo/tr_boun/v2.11/treebank.json
echo End date and time: $(date)

RET=$?

exit $RET
