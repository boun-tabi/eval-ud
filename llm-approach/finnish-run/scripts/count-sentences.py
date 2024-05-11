import argparse, os, subprocess, re
from pathlib import Path

def clone_repo(treebank, treebank_dir):
    treebank_url = f'https://github.com/UniversalDependencies/{treebank}.git'
    subprocess.run(['git', 'clone', treebank_url, treebank_dir])
    if not treebank_dir.exists():
        print('Treebank {treebank} not cloned.'.format(treebank=treebank))
        exit()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tb', '--treebank', type=str, required=True)
    parser.add_argument('-v', '--version', type=str, required=True)
    parser.add_argument('-d', '--data_dir', type=str, required=True)
    return parser.parse_args()

def get_sentence_count(conllu_files):
    sent_count = 0
    for conllu_file in conllu_files:
        with conllu_file.open('r', encoding='utf-8') as f:
            content = f.read()
        sents = content.split('\n\n')
        sent_count += len(sents)
    return sent_count

def main():
    THIS_DIR = Path.cwd()
    args = get_args()

    tag_pattern = re.compile(r'^r(\d+\.\d+)$')

    if not (args.treebank and args.version and args.data_dir):
        print('Please specify a treebank, a data directory and a version.')
        exit()
    data_dir = Path(args.data_dir)
    treebank = args.treebank
    version = args.version
    treebank_dir = data_dir / treebank
    if not treebank_dir.exists():
        clone_repo(treebank, treebank_dir)
    os.chdir(treebank_dir)
    tags = [i for i in subprocess.check_output(['git', 'tag', '-l']).decode('utf-8').strip().split('\n') if i and tag_pattern.match(i)]
    current_tag = f'r{version}'
    if current_tag not in tags:
        print('Tag {tag} not found.'.format(tag=current_tag))
        exit()
    subprocess.run(['git', 'checkout', current_tag])
    os.chdir(THIS_DIR)
    conllu_files = list(treebank_dir.glob('*.conllu'))
    sent_count = get_sentence_count(conllu_files)
    print(treebank, version, sent_count)
    
if __name__ == '__main__':
    main()
