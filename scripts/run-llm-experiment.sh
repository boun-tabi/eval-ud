#!/bin/bash
#SBATCH --job-name=eval-ud
#SBATCH --output=outs/%j.log
#SBATCH --container-image ghcr.io\#bouncmpe/cuda-python3
#SBATCH --time=7-00:00:00

source /opt/python3/venv/base/bin/activate

cd ~/eval-ud
pip install -r llm-approach/requirements.txt

python3 llm-approach/finnish-run/scripts/run-llm-experiment.py -r RUN_DIR

