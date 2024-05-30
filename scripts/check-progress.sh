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
        echo $dir
        echo "File does not exist"
        echo "----------------"
        continue
    fi
    sent_id_count=$(cat $tb_output_file | grep sent_id | wc -l)
    # if not 500
    if [ $sent_id_count -ne 500 ]
    then
        echo $dir
        echo $sent_id_count
        echo "----------------"
    fi
done
