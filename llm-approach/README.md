# llm-approach

Call the eventual experiment first with the following command:

```bash
python3 llm-approach/eventual-experiment.py -t8 tr_boun/v2.8/treebank.json -t11 tr_boun/v2.11/treebank.json -s llm-approach/selected_sents.json -m MODEL_NAME
```

If all the sentences did not return outputs, due to rate limits, then run the following command till all 500 sentences are processed:

```bash
python3 llm-approach/eventual-experiment.py -r llm-approach/experiment_outputs/eventual_experiment/EXPERIMENT_DIR
```
