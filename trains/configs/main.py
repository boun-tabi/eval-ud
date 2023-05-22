import argparse, os, json

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

config_path = os.path.join(THIS_DIR, str(os.environ.get('SLURM_JOB_ID')) + '.json')
print(config_path)

parser = argparse.ArgumentParser()
parser.add_argument('--train-type', action='store', dest='train_type', required=True)
parser.add_argument('--treebank', action='store', dest='treebank', required=True)
args = parser.parse_args()

with open(os.path.join(THIS_DIR, 'vanilla-config.json'), 'r') as f:
    config = json.load(f)

config['experiment'] = args.treebank
config['name'] = args.train_type

config['train_type'] = args.train_type
config['treebank'] = args.treebank

repo_path = '/clusterusers/furkan.akkurt@boun.edu.tr/eval-ud/gitlab-repo'

tb_folder = os.path.join(repo_path, 'trains/tbs', args.treebank)
train_path = os.path.join(tb_folder, 'train.conllu')
config['data_loaders']['paths']['train'] = train_path
dev_path = os.path.join(tb_folder, 'dev.conllu')
config['data_loaders']['paths']['dev'] = dev_path
test_path = os.path.join(tb_folder, 'test.conllu')
config['data_loaders']['paths']['test'] = test_path

vocab_folder = os.path.join(repo_path, 'trains/vocabs', args.treebank)

feats_on = False
lemma_on = False
pos_on = False
deps_on = False
form_on = False
aux_l = list()
target = str()

if args.train_type == 'feats-only':
    feats_on = True
    target = 'ufeats'
elif args.train_type == 'lemma-only':
    lemma_on = True
    target = 'lemma'
elif args.train_type == 'pos-only':
    pos_on = True
    target = 'upos'
elif args.train_type == 'dep-parsing':
    deps_on = True
    target = 'dep'
elif args.train_type == 'dep-parsing_feats':
    deps_on = True
    feats_on = True
    aux_l = ['ufeats']
    target = 'dep'
elif args.train_type == 'dep-parsing_lemma':
    deps_on = True
    lemma_on = True
    aux_l = ['lemma']
    target = 'dep'
elif args.train_type == 'dep-parsing_upos':
    deps_on = True
    pos_on = True
    aux_l = ['upos']
    target = 'dep'
elif args.train_type == 'dep-parsing_upos_feats':
    deps_on = True
    pos_on = True
    feats_on = True
    aux_l = ['upos', 'ufeats']
    target = 'dep'
elif args.train_type == 'upos_feats':
    feats_on = True
    pos_on = True
    aux_l = ['upos']
    target = 'ufeats'
elif args.train_type == 'feats_lemma':
    feats_on = True
    lemma_on = True
    aux_l = ['ufeats']
    target = 'lemma'
elif args.train_type == 'form':
    form_on = True
    deps_on = True
    pos_on = True
    feats_on = True
    lemma_on = True
    aux_l = ['upos', 'ufeats', 'lemma', 'heads', 'labels']
    target = 'form'

if feats_on:
    config['model']['args']['outputs']['ufeats'] = { 'type': 'SequenceTagger', 'args': { 'hidden_size': 0, 'input_dropout': 0.2, 'vocab': { 'type': 'BasicVocab', 'args': { 'vocab_filename': os.path.join(vocab_folder, 'feats.vocab') } } } }
    config['data_loaders']['args']['annotation_layers']['ufeats'] = { 'type': 'TagSequence', 'source_column': 5, 'args': { 'ignore_root': True } }
if lemma_on:
    config['model']['args']['outputs']['lemma'] = { 'type': 'SequenceTagger', 'args': { 'hidden_size': 0, 'input_dropout': 0.2, 'vocab': { 'type': 'BasicVocab', 'args': { 'vocab_filename': os.path.join(vocab_folder, 'lemma.vocab') } } } }
    config['data_loaders']['args']['annotation_layers']['lemma'] = { 'type': 'TagSequence', 'source_column': 2, 'args': { 'ignore_root': True } }
if pos_on:
    config['model']['args']['outputs']['upos'] = { 'type': 'SequenceTagger', 'args': { 'hidden_size': 0, 'input_dropout': 0.2, 'vocab': { 'type': 'BasicVocab', 'args': { 'vocab_filename': os.path.join(vocab_folder, 'pos.vocab') } } } }
    config['data_loaders']['args']['annotation_layers']['upos'] = { 'type': 'TagSequence', 'source_column': 3, 'args': { 'ignore_root': True } }
if deps_on:
    config['model']['args']['outputs']['heads'] = { 'type': 'ArcScorer', 'args': { 'scorer_class': 'DeepBiaffineScorer', 'head_mode': 'single_head', 'hidden_size': 1024, 'dropout': 0.33, 'vocab': { 'type': 'IntegerVocab' } } }
    config['model']['args']['outputs']['labels'] = { 'type': 'DependencyClassifier', 'args': { 'scorer_class': 'DeepBiaffineScorer', 'hidden_size': 256, 'dropout': 0.33, 'vocab': { 'type': 'BasicVocab', 'args': { 'vocab_filename': os.path.join(vocab_folder, 'deprel.vocab') } } } }
    config['data_loaders']['args']['annotation_layers']['heads'] = { 'type': 'TagSequence', 'source_column': 6, 'args': { 'ignore_root': True } }
    config['data_loaders']['args']['annotation_layers']['labels'] = { 'type': 'DependencyMatrix', 'source_column': [6, 7], 'args': { 'ignore_non_relations': True } }
    config['model']['args']['post_processors'] = [ { 'type': 'FactorizedMSTPostProcessor', 'args': { 'annotation_ids': [ 'heads', 'labels' ] } } ]
if form_on:
    config['model']['args']['outputs']['form'] = { 'type': 'SequenceTagger', 'args': { 'hidden_size': 0, 'input_dropout': 0.2, 'vocab': { 'type': 'BasicVocab', 'args': { 'vocab_filename': os.path.join(vocab_folder, 'form.vocab') } } } }
    config['data_loaders']['args']['annotation_layers']['form'] = { 'type': 'TagSequence', 'source_column': 1, 'args': { 'ignore_root': True } }

if target == 'ufeats':
    config['trainer']['validation_criterion']['metrics'] = { 'ufeats': 'fscore' }
elif target == 'upos':
    config['trainer']['validation_criterion']['metrics'] = { 'upos': 'fscore' }
elif target == 'lemma':
    config['trainer']['validation_criterion']['metrics'] = { 'lemma': 'fscore' }
elif target == 'dep':
    config['trainer']['validation_criterion']['metrics'] = { 'heads': 'fscore', 'labels': 'fscore' }
elif target == 'form':
    config['trainer']['validation_criterion']['metrics'] = { 'form': 'fscore' }

for aux in aux_l:
    config['trainer']['loss_scaling'][aux] = 'lambda epoch: 0.05'

with open(config_path, 'w') as f:
    json.dump(config, f, indent=4)