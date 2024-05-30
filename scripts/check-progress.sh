main_dir="llm-approach/finnish-run/scripts/outputs"
dirs=(
    "poe_Claude-2-100k-UD_Turkish-BOUN-2.11-2024-05-28_14-07-41"
    "poe_Claude-2-100k-UD_Turkish-BOUN-2.8-2024-05-28_13-15-11"
    "poe_Claude-3-Opus-200k-UD_Turkish-BOUN-2.11-2024-05-28_17-04-17"
    "poe_Claude-3-Opus-200k-UD_Turkish-BOUN-2.8-2024-05-28_15-59-41"
    "poe_Claude-instant-100k-UD_Turkish-BOUN-2.11-2024-05-28_11-38-41"
    "poe_Claude-instant-100k-UD_Turkish-BOUN-2.8-2024-05-28_00-37-10"
    "poe_Llama-2-70b-UD_Turkish-BOUN-2.11-2024-05-28_18-49-41"
    "poe_Llama-2-70b-UD_Turkish-BOUN-2.8-2024-05-28_18-07-41"
    "poe_GPT-3.5-Turbo-UD_Turkish-BOUN-2.8-2024-05-28_22-58-45"
)

for dir in "${dirs[@]}"
do
    echo $dir
    cat $main_dir/$dir/tb_output.json | grep sent_id | wc -l
done
