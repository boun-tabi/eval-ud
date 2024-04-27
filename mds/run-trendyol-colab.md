# Commands to run TrendyolLLM experiment on Colab

1. Generate SSH key to clone the repository:

    ```bash
        ssh-keygen
    ```

2. Copy the SSH key to the clipboard:

    ```bash
        cat ~/.ssh/id_rsa.pub
    ```

3. Add the SSH key to the GitLab account, [here](https://gitlab.com/-/user_settings/ssh_keys).

4. Clone the repository:

    ```bash
        git clone git@gitlab.com:nlpgroup1/eval-ud.git
    ```

5. Change the directory to the repository:

    ```bash
        cd eval-ud
    ```

6. Install the required packages:

    ```bash
        pip install -r llm-approach/requirements.txt
    ```

7. Run the TrendyolLLM experiment:

    ```bash
        # either start a new experiment
        python3 llm-approach/finnish-run/scripts/run-llm-experiment.py --sent-count 500 -d util/ud-docs -lp llm-approach/data/langs.json -l LANGUAGE_CODE -v TREEBANK_VERSION --data-dir llm-approach/finnish-run/data -tb TREEBANK -m trendyol_Trendyol-LLM-7b-chat-v1.0
        # or continue a previous experiment
        python3 llm-approach/finnish-run/scripts/run-llm-experiment.py -r RUN_DIR
    ```

8. Introduce yourself to `git`:

    ```bash
        git config --global user.email EMAIL
        git config --global user.name NAME
    ```