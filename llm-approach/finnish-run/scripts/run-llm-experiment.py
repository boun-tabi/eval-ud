from datetime import datetime
import os, json, argparse, logging
from pathlib import Path
from templates import get_sentence_prompt, template_sentence_with_dep

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tb', '--treebank', type=str)
    parser.add_argument('-r', '--run-dir', type=str)
    parser.add_argument('-s', '--sents', type=str)
    parser.add_argument('-m', '--model', type=str)
    parser.add_argument('-n', '--note', type=str)
    parser.add_argument('-d', '--docs', type=str)
    parser.add_argument('-k', '--api-key', type=str)
    parser.add_argument('-lp', '--langs-path', type=str)
    parser.add_argument('-l', '--language', type=str)
    return parser.parse_args()

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    THIS_DIR = Path(__file__).resolve().parent
    logging.basicConfig(filename=THIS_DIR / 'run-llm-experiment.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')
    return logger

def main():
    args = get_args()

    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    logger = get_logger()
    logger.info('Started at {now}'.format(now=now))

    script_path = Path(__file__).resolve()
    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()
    THIS_DIR = script_path.parent

    if args.run_dir:
        run_dir = Path(args.run_dir)
        logger.info('Using run directory {run_dir}'.format(run_dir=run_dir))
        with open(run_dir / 'md.json', 'r', encoding='utf-8') as f:
            md = json.load(f)
        model = md['model']
        tb = Path(md['tb'])
        sents = md['sents']
        sentence_count = md['sentence_count']
        docs_dir = Path(md['docs_dir'])
        api_path = Path(md['api_path'])
        language = md['language']
        langs_path = Path(md['langs_path'])
        with open(langs_path, 'r', encoding='utf-8') as f:
            langs = json.load(f)
    else:
        output_dir = THIS_DIR / 'outputs'
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
        run_dir = output_dir / '{model}-{now}'.format(model=model, now=now)
        os.makedirs(run_dir, exist_ok=True)
        with open(run_dir / 'script.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        if args.treebank:
            tb = Path(args.treebank)
        else:
            logger.info('Please specify a treebank.')
            exit()
        if args.sents:
            sents_path = Path(args.sents)
            with open(sents_path, 'r', encoding='utf-8') as f:
                sents = json.load(f)
            sentence_count = len(sents)
        else:
            logger.info('Please specify a sentence list.')
            exit()
        api_path = args.api_key
        with open(run_dir / 'md.json', 'w', encoding='utf-8') as f:
            md = {'sentence_count': sentence_count, 'sents': sents, 'model': model, 'now': now, 'run_dir': str(run_dir), 'tb': str(tb), 'docs_dir': str(docs_dir), 'script_path': str(script_path), 'api_path': str(api_path), 'language': language, 'langs_path': str(langs_path)}
            md['prompt'] = template_sentence_with_dep
            if args.note:
                md['note'] = args.note
            json.dump(md, f, ensure_ascii=False, indent=2)

    with open(docs_dir / 'pos-{language}.json'.format(language=language), 'r', encoding='utf-8') as f:
        pos_d = json.load(f)
    with open(docs_dir / 'feat-{language}.json'.format(language=language), 'r', encoding='utf-8') as f:
        feat_d = json.load(f)
    with open(docs_dir / 'dep-{language}.json'.format(language=language), 'r', encoding='utf-8') as f:
        dep_d = json.load(f)

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

    with open(tb, 'r', encoding='utf-8') as f:
        tb_data = json.load(f)
    table_d = tb_data

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
    for i, sent_id in enumerate(sents):
        print('Processing {i} of {count}.'.format(i=i, count=sentence_count))
        output = ''
        if sent_id in tb_done_sents:
            continue
        text, table = table_d[sent_id]['text'], table_d[sent_id]['table']
        prompt = get_sentence_prompt(template_sentence_with_dep, langs[language], table, pos_d, feat_d, dep_d)
        d = {'sent_id': sent_id, 'text': text, 'prompt': prompt}
        if model.startswith('poe'):
            try:
                if model == 'poe_GPT-4':
                    output = asyncio.run(get_response(prompt, 'GPT-4', api_key))
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
    if output_l_len != sentence_count:
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