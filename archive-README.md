## Running of script for categorizing errors, `util/categorize_errors.py`

`regex` module is needed which can be installed with `pip install -r requirements.txt`. A virtual environment is recommended. The following can be run to categorize errors of a given treebank (`python` becomes `python3` for UNIX systems) in the root directory of the cloned repository: `python CATEGORIZE_ERRORS_SCRIPT_PATH --conllu CONLLU_PATH`

The _conllu_ flag is required. The flags _errors_ and _ud-validation_ are optional. If the error folder path is not given, an `Errors` folder is created in the directory of the script. The given error folder path need not exist; if it doesn't exist, it'll be created. If the _ud-validation_ flag is not used, `validate.py` script in the script's directory is used.

The validation script path: `util/validate.py`. Error-categorizing script's path: `util/categorize_errors.py`.

## Miscellaneous

The script `util/evaluate_morp_in_conllu.py` works as: `python3 evaluate_morp_in_conllu.py gold_file pred_file morp_col_gold morp_col_pred`.
