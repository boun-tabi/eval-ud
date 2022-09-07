# BOUN Treebank Evaluation Project

**Name**: BOUN Treebank Evaluation  
**Description**: This project aims to execute and document the evaluation of BOUN Treebank, after its reannotation in 2021-22.

## Running of script for categorizing errors, `util/categorize_errors.py`

The following can be run to categorize errors of a given treebank (python becomes python3 for UNIX systems) in the root directory of the cloned repository; `regex` module is needed which can be installed with `pip install -r requirements.txt`:

```
python CATEGORIZE_ERRORS_SCRIPT_PATH --errors ERROR_FOLDER_PATH --ud-validation VALIDATION_SCRIPT_PATH --conllu CONLLU_PATH
```

The _errors_, _ud-validation_ and _conllu_ flags are all required. The error folder path need not exist; if it doesn't exist, it'll be created.

The validation script path: `util/validate.py`. The script's path for categorizing errors: `util/categorize_errors.py`.
