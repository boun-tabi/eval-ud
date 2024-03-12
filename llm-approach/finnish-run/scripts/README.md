# How to run the Finnish experiment

1. Install the required packages by running `pip install -r llm-approach/requirements.txt`.
2. In the root directory of the repository, run the command below (prompts GPT-4):

    ```bash
        python3 llm-approach/finnish-run/scripts/run-llm-experiment.py -tb llm-approach/finnish-run/data/treebank.json -s llm-approach/finnish-run/data/selected_sents.json -m poe_GPT-4 -d util/ud-docs/data/ -k llm-approach/keys/poe.json -lp llm-approach/data/langs.json -l fi
    ```

3. Clean the output by the command below:

    ```bash
        python3 llm-approach/finnish-run/scripts/clean_output.py -o llm-approach/finnish-run/scripts/outputs/SPECIFIC_RUN_DIR/tb_output.json
    ```

4. Summarize the experiment with sequence matching:

    ```bash
        python3 llm-approach/finnish-run/scripts/summarize_experiment-sequence_matching.py -r llm-approach/finnish-run/scripts/outputs/SPECIFIC_RUN_DIR
    ```

5. Compare the token accuracy with:

    ```bash
        python3 llm-approach/finnish-run/scripts/compare-tokens.py -d llm-approach/finnish-run/scripts/outputs/SPECIFIC_RUN_DIR
    ```
