#!/bin/bash
#SBATCH --job-name=eval-ud
#SBATCH --output=outs/%j.log
#SBATCH --container-image ghcr.io\#bouncmpe/cuda-python3
#SBATCH --time=7-00:00:00
#SBATCH --gpus=1
#SBATCH --cpus-per-gpu=8
#SBATCH --mem-per-gpu=80G

source /opt/python3/venv/base/bin/activate

cd ~/eval-ud
pip install -r llm-approach/requirements.txt
pip install sentencepiece protobuf==3.20.0

python3 llm-approach/finnish-run/scripts/run-llm-experiment.py -r llm-approach/finnish-run/scripts/outputs/trendyol_Trendyol-LLM-7b-chat-v1.0-UD_Turkish-BOUN-2.8-2024-04-27_16-49-11

