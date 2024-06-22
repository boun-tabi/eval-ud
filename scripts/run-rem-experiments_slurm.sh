#!/bin/bash
#SBATCH --job-name=eval-ud
#SBATCH --output=outs/%j.log
#SBATCH --container-image ghcr.io\#bouncmpe/cuda-python3
#SBATCH --time=7-00:00:00

source /opt/python3/venv/base/bin/activate

cd ~/eval-ud
pip install fastapi-poe
echo "Dependencies installed"

main_dir="llm-approach/finnish-run/scripts/outputs"

# get only directories
dirs=($(ls -d $main_dir/*/))

# iterate over all directories
for dir in "${dirs[@]}"
do
    tb_output_file="$dir/tb_output.json"
    # if file does not exist
    if [ ! -f $tb_output_file ]
    then
        echo 'File does not exist for' $dir
        echo Running $dir
        python3 llm-approach/finnish-run/scripts/run-llm-experiment.py -r $dir
    fi
    sent_id_count=$(cat $tb_output_file | grep sent_id | wc -l)
    # if not 500
    if [ $sent_id_count -ne 500 ]
    then
        echo 'Sent ID count is not 500 for' $dir
        echo Running $dir
        python3 llm-approach/finnish-run/scripts/run-llm-experiment.py -r $dir
    fi
done
