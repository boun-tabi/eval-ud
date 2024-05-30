#!/bin/bash
#SBATCH --job-name=eval-ud
#SBATCH --output=outs/%j.log
#SBATCH --container-image ghcr.io\#bouncmpe/cuda-python3
#SBATCH --time=7-00:00:00

source /opt/python3/venv/base/bin/activate

cd ~/eval-ud
pip install -r llm-approach/requirements.txt

models=( "poe_GPT-3.5-Turbo" "poe_Mistral-Large" "poe_Mistral-Medium" "poe_Mixtral-8x7B-Chat" )
versions=( "2.8" "2.11" )

for model in "${models[@]}"
do
    for version in "${versions[@]}"
    do
        python3 llm-approach/finnish-run/scripts/run-llm-experiment.py --sent-count 500 -d util/ud-docs --ud-docs ~/repos/ud/docs -k llm-approach/keys/poe.json -lp llm-approach/data/langs.json --data-dir llm-approach/finnish-run/data --has-dependency -m $model -l tr -tb UD_Turkish-BOUN -v $version
    done
done

