from datetime import datetime
import os, json, argparse, logging, subprocess, re, random, sys
from pathlib import Path
from templates import get_sentence_prompt, get_example_prompt, template_sentence

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tb', '--treebank', type=str)
    parser.add_argument('--data-dir', type=str)
    parser.add_argument('-r', '--run-dir', type=str)
    parser.add_argument('--sent-count', type=str)
    parser.add_argument('-m', '--model', type=str)
    parser.add_argument('-n', '--note', type=str)
    parser.add_argument('-d', '--docs', type=str)
    parser.add_argument('-k', '--api-key', type=str)
    parser.add_argument('-lp', '--langs-path', type=str)
    parser.add_argument('-l', '--language', type=str)
    parser.add_argument('-v', '--version', type=str)
    parser.add_argument('--ud-docs', type=str)
    parser.add_argument('--has-dependency', action='store_true')
    parser.add_argument('--special-tr', action='store_true')
    return parser.parse_args()

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    script_dir = Path(__file__).resolve().parent
    logging.basicConfig(filename=script_dir / 'run-llm-experiment.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')
    return logger

def get_treebank(conllu_files):
    data_d = {'sentences': {}}
    md_pattern = re.compile('^# (.+?) = (.+?)$')
    annotation_pattern = re.compile('(.+\t){9}.+')
    for conllu_file in conllu_files:
        with conllu_file.open('r', encoding='utf-8') as f:
            content = f.read()
        sents = content.split('\n\n')
        for sent in sents:
            lines = sent.split('\n')
            sent_id = ''
            d_t = {}
            for i, line in enumerate(lines):
                md_match = md_pattern.match(line)
                if md_match:
                    field = md_match.group(1).strip()
                    value = md_match.group(2).strip()
                    if field == 'sent_id':
                        sent_id = value
                    else:
                        d_t[field] = value
                annotation_match = annotation_pattern.match(line)
                if annotation_match:
                    annotation = '\n'.join(lines[i:])
                    d_t['table'] = annotation
                    break
            if d_t:
                data_d['sentences'][sent_id] = d_t
    return data_d

def main():
    THIS_DIR = Path.cwd()
    args = get_args()

    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    logger = get_logger()
    logger.info('Started at {now}'.format(now=now))

    script_path = Path(__file__).relative_to(THIS_DIR)
    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()
    script_dir = script_path.parent
    tag_pattern = re.compile(r'^r(\d+\.\d+)$')

    if args.run_dir:
        run_dir = Path(args.run_dir)
        logger.info('Using run directory {run_dir}'.format(run_dir=run_dir))
        with open(run_dir / 'md.json', 'r', encoding='utf-8') as f:
            md = json.load(f)
        model = md['model']
        data_dir = Path(md['data_dir'])
        treebank = md['treebank']
        sent_count = md['sent_count']
        tb_dir = data_dir / treebank
        sent_ids_path = data_dir / 'sent_ids/{treebank}-{sent_count}.json'.format(treebank=treebank, sent_count=sent_count)
        if sent_ids_path.exists():
            with sent_ids_path.open('r', encoding='utf-8') as f:
                content = json.load(f)
                sent_ids = content['sent_ids']
                example_sent_id = content['example_sent_id']
        else:
            sent_ids = md['sent_ids']
            example_sent_id = md['example_sent_id']
        version = md['version']
        os.chdir(tb_dir)
        tags = [i for i in subprocess.check_output(['git', 'tag', '-l']).decode('utf-8').strip().split('\n') if i and tag_pattern.match(i)]
        current_tag = f'r{version}'
        if current_tag not in tags:
            logger.info('Tag {tag} not found.'.format(tag=current_tag))
            exit()
        subprocess.run(['git', 'checkout', current_tag])
        os.chdir(THIS_DIR)
        conllu_files = list(tb_dir.glob('*.conllu'))
        tb_d = get_treebank(conllu_files)
        docs_dir = Path(md['docs_dir'])
        api_path = Path(md['api_path'])
        language = md['language']
        langs_path = Path(md['langs_path'])
        with langs_path.open('r', encoding='utf-8') as f:
            langs = json.load(f)
        if md['dependency_included']:
            from templates import preamble_dep as preamble
        else:
            from templates import preamble_no_dep as preamble
        preamble = preamble.format(language=langs[language])
        template = template_sentence
    else:
        if not args.treebank or not args.sent_count or not args.docs or not args.api_key or not args.langs_path or not args.language or not args.version:
            logger.info('Please specify a treebank, a sentence count, a docs directory, an API key, a language, and a version.')
            exit()
        sent_count = int(args.sent_count)
        data_dir = Path(args.data_dir)
        treebank = args.treebank
        version = args.version
        treebank_dir = data_dir / treebank
        if not treebank_dir.exists():
            treebank_url = f'https://github.com/UniversalDependencies/{treebank}.git'
            subprocess.run(['git', 'clone', treebank_url, treebank_dir])
            if not treebank_dir.exists():
                logger.info('Treebank {treebank} not cloned.'.format(treebank=treebank))
                exit()
        os.chdir(treebank_dir)
        tags = [i for i in subprocess.check_output(['git', 'tag', '-l']).decode('utf-8').strip().split('\n') if i and tag_pattern.match(i)]
        current_tag = f'r{version}'
        if current_tag not in tags:
            logger.info('Tag {tag} not found.'.format(tag=current_tag))
            exit()
        subprocess.run(['git', 'checkout', current_tag])
        os.chdir(THIS_DIR)
        conllu_files = list(treebank_dir.glob('*.conllu'))
        tb_d = get_treebank(conllu_files)

        sent_ids_path = data_dir / 'sent_ids/{treebank}-{sent_count}.json'.format(treebank=treebank, sent_count=sent_count)
        if sent_ids_path.exists():
            with sent_ids_path.open('r', encoding='utf-8') as f:
                content = json.load(f)
                sent_ids = content['sent_ids']
                example_sent_id = content['example_sent_id']
        else:
            all_sent_ids = list(tb_d['sentences'].keys())
            sent_ids = []
            while len(sent_ids) < sent_count:
                new_id = random.choice(all_sent_ids)
                table = tb_d['sentences'][new_id]['table']
                token_count = len([line for line in table.split('\n') if '-' not in line.split('\t')[0]])
                if new_id not in sent_ids and token_count < 30:
                    sent_ids.append(new_id)
            token_count_OK = False
            while not token_count_OK:
                example_sent_id = random.choice(list(set(all_sent_ids).difference(sent_ids)))
                example_table = tb_d['sentences'][example_sent_id]['table']
                token_count = len([line for line in example_table.split('\n') if '-' not in line.split('\t')[0]])
                if 5 < token_count < 10:
                    token_count_OK = True
            with sent_ids_path.open('w', encoding='utf-8') as f:
                json.dump({'sent_ids': sent_ids, 'example_sent_id': example_sent_id}, f, ensure_ascii=False, indent=2)

        output_dir = script_dir / 'outputs'
        docs_dir = Path(args.docs)
        if args.model:
            model = args.model
        else:
            logger.info('Please specify a model.')
            exit()
        if args.langs_path:
            langs_path = Path(args.langs_path)
            language = args.language
            with open(langs_path, 'r', encoding='utf-8') as f:
                langs = json.load(f)
            if language not in langs:
                logger.info('Please specify a language.')
                exit()
        run_dir = output_dir / '{model}-{treebank}-{version}-{now}'.format(model=model, treebank=treebank, version=version, now=now)
        os.makedirs(run_dir, exist_ok=True)
        with open(run_dir / 'script.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        api_path = args.api_key
        with open(run_dir / 'md.json', 'w', encoding='utf-8') as f:
            md = {'sent_count': sent_count, 'sent_ids': sent_ids, 'example_sent_id': example_sent_id, 'model': model, 'now': now, 'run_dir': str(run_dir), 'treebank': treebank, 'docs_dir': str(docs_dir), 'script_path': str(script_path), 'api_path': str(api_path), 'language': language, 'langs_path': str(langs_path), 'data_dir': str(data_dir), 'version': version}
            if args.has_dependency:
                md['dependency_included'] = True
                from templates import preamble_dep as preamble
            else:
                md['dependency_included'] = False
                from templates import preamble_no_dep as preamble
            preamble = preamble.format(language=langs[language])
            if args.special_tr:
                md['special_tr'] = True
                preamble += ' Lemma "y" represents the overt copula in Turkish and surfaces as "i".'
            md['preamble'] = preamble
            md['prompt'] = template_sentence
            template = template_sentence
            if args.note:
                md['note'] = args.note
            json.dump(md, f, ensure_ascii=False, indent=2)

    docs_data_dir = docs_dir / 'data'
    pos_path = docs_data_dir / 'pos-{language}.json'.format(language=language)
    feat_path = docs_data_dir / 'feat-{language}.json'.format(language=language)
    dep_path = docs_data_dir / 'dep-{language}.json'.format(language=language)
    if not pos_path.exists() or not feat_path.exists() or not dep_path.exists():
        get_docs_script_path = docs_dir / 'scripts/get_docs.py'
        if not args.ud_docs:
            logger.info('Please specify a UD docs directory.')
            exit()
        subprocess.run([sys.executable, get_docs_script_path, '-l', language, '-d', args.ud_docs, '-o', docs_data_dir])
        if not pos_path.exists() or not feat_path.exists() or not dep_path.exists():
            logger.info('Docs not generated.')
            exit()
    with pos_path.open('r', encoding='utf-8') as f:
        pos_d = json.load(f)
    with feat_path.open('r', encoding='utf-8') as f:
        feat_d = json.load(f)
    if args.has_dependency:
        with dep_path.open('r', encoding='utf-8') as f:
            dep_d = json.load(f)
    else:
        dep_d = None

    if model.startswith('poe'):
        with open(api_path) as f:
            poe_d = json.load(f)
        api_key = poe_d['token']
        from fastapi_poe.types import ProtocolMessage
        from fastapi_poe.client import get_bot_response
        import asyncio
        async def get_response(prompt, bot_name, api_key):
            message = ProtocolMessage(role='user', content=prompt)
            output = ''
            async for partial in get_bot_response(messages=[message], bot_name=bot_name, api_key=api_key):
                output += partial.text
            return output
    else:
        exit('Unknown model: {model}'.format(model=model))

    table_d = tb_d['sentences']
    tb_out = run_dir / 'tb_output.json'
    if tb_out.exists():
        with open(tb_out, 'r', encoding='utf-8') as f:
            tb_output = json.load(f)
    else:
        tb_output = []
    tb_done_sents = [d['sent_id'] for d in tb_output]
    run_done = True
    asked_count = 0
    output_l = tb_output
    example_token, example_input = get_example_prompt(tb_d['sentences'][example_sent_id]['table'], pos_d, feat_d, dep_d, args.special_tr)
    example_text = tb_d['sentences'][example_sent_id]['text']
    for i, sent_id in enumerate(sent_ids):
        print('Processing {i} of {count}.'.format(i=i, count=sent_count))
        output = ''
        if sent_id in tb_done_sents:
            continue
        text, table = table_d[sent_id]['text'], table_d[sent_id]['table']
        prompt = get_sentence_prompt(template, preamble, example_text, example_token, example_input, langs[language], table, pos_d, feat_d, dep_d)
        d = {'sent_id': sent_id, 'text': text, 'prompt': prompt}
        if model.startswith('poe'):
            try:
                specific_model = model.replace('poe_', '')
                output = asyncio.run(get_response(prompt, specific_model, api_key))
            except:
                continue
            d['output'] = output
        else:
            print('Unknown model: {model}'.format(model=model))
            d['output'] = ''
        if d['output'] == '':
            continue
        output_l.append(d)
        asked_count += 1
        with open(tb_out, 'w', encoding='utf-8') as f:
            json.dump(output_l, f, ensure_ascii=False, indent=4)
    with open(tb_out, 'w', encoding='utf-8') as f:
        json.dump(output_l, f, ensure_ascii=False, indent=4)
    print('Asked {count} questions.'.format(count=asked_count))
    output_l_len = len(output_l)
    print('Output length: {len}'.format(len=output_l_len))
    if output_l_len != sent_count:
        run_done = False
        print('Not all tokens are done.')
    else:
        print('All tokens are done.')
    if run_done:
        print('All done.')
    else:
        print('Not all done.')
        os.system('python3 {script_path} -r {run_dir}'.format(script_path=script_path, run_dir=run_dir))
    logger.info('Ended at {now}'.format(now=datetime.now().strftime('%Y%m%d%H%M%S')))

if __name__ == '__main__':
    main()