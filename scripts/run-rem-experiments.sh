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
        python3 llm-approach/finnish-run/scripts/run-llm-experiment.py -r $dir -t 3
    fi
done
