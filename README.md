# BOUN Treebank Evaluation Project

**Name**: BOUN Treebank Evaluation  
**Description**: This project aims to execute and document the evaluation of BOUN Treebank, after its reannotation in 2021-22.

## Running of script for categorizing errors, `util/categorize_errors.py`

`regex` module is needed which can be installed with `pip install -r requirements.txt`. A virtual environment is recommended. The following can be run to categorize errors of a given treebank (`python` becomes `python3` for UNIX systems) in the root directory of the cloned repository: `python CATEGORIZE_ERRORS_SCRIPT_PATH --conllu CONLLU_PATH`

The _conllu_ flag is required. The flags _errors_ and _ud-validation_ are optional. If the error folder path is not given, an `Errors` folder is created in the directory of the script. The given error folder path need not exist; if it doesn't exist, it'll be created. If the _ud-validation_ flag is not used, `validate.py` script in the script's directory is used.

The validation script path: `util/validate.py`. The script's path for categorizing errors: `util/categorize_errors.py`.
