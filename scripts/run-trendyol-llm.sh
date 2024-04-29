#!/bin/bash
#SBATCH --job-name=eval-ud
#SBATCH --output=outs/%j.log
#SBATCH --container-image ghcr.io\#bouncmpe/cuda-python3
#SBATCH --time=7-00:00:00
#SBATCH --gpus=1
#SBATCH --cpus-per-gpu=12
#SBATCH --mem-per-gpu=60G

source /opt/python3/venv/base/bin/activate

cd ~/eval-ud
pip install -r llm-approach/requirements.txt

python3 llm-approach/finnish-run/scripts/run-llm-experiment.py --sent-count 500 -d util/ud-docs -lp llm-approach/data/langs.json -l tr -v 2.11 --data-dir llm-approach/finnish-run/data -tb UD_Turkish-BOUN -m trendyol_Trendyol-LLM-7b-chat-v1.0 --has-dependency

